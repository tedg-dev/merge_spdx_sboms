import click
import sys
from pathlib import Path
from .__version__ import __version__
from .services.merger import SbomMerger
from .services.parser import SpdxParser
from .services.reporter import MergeReporter
from .services.spdx_spec_validator import SpdxSpecValidator
from .infrastructure.config import Config
from .infrastructure.file_handler import FileHandler
from .infrastructure.github_client import GitHubClient


@click.command()
@click.option(
    "--dependencies-dir",
    type=click.Path(exists=True, path_type=Path),
    required=True,
    help="Path to dependencies directory containing dependency SBOMs",
)
@click.option(
    "--output-dir",
    type=click.Path(path_type=Path),
    default=None,
    help="Output directory for merged SBOM (default: same as root SBOM)",
)
@click.option(
    "--key-file",
    type=click.Path(),
    default="keys.json",
    help="Path to keys.json file for GitHub authentication",
)
@click.option(
    "--account", type=str, default=None, help="GitHub account username from keys.json"
)
@click.option(
    "--push-to-github", is_flag=True, help="Push merged SBOM to GitHub repository"
)
@click.option(
    "--github-owner",
    type=str,
    default=None,
    help="GitHub repository owner (required with --push-to-github)",
)
@click.option(
    "--github-repo",
    type=str,
    default=None,
    help="GitHub repository name (required with --push-to-github)",
)
@click.option(
    "--github-path",
    type=str,
    default="sboms/merged_sbom.json",
    help="Target path in GitHub repository",
)
@click.option(
    "--github-branch",
    type=str,
    default="main",
    help="GitHub branch to push to (default: main)",
)
@click.option("--verbose", is_flag=True, help="Enable verbose output")
def main(
    dependencies_dir,
    output_dir,
    key_file,
    account,
    push_to_github,
    github_owner,
    github_repo,
    github_path,
    github_branch,
    verbose,
):
    click.echo("=" * 70)
    click.echo(f"SPDX SBOM Merger v{__version__}")
    click.echo("=" * 70)

    try:
        if verbose:
            click.echo(f"\n🔍 Discovering SBOM files in: {dependencies_dir}")

        root_sbom, dep_sboms = FileHandler.discover_sbom_files(dependencies_dir)

        if verbose:
            click.echo(f"✅ Found root SBOM: {root_sbom.name}")
            click.echo(f"✅ Found {len(dep_sboms)} dependency SBOMs")

        click.echo(f"\n📦 Root SBOM: {root_sbom.name}")
        click.echo(f"📦 Dependency SBOMs: {len(dep_sboms)}")

        # Estimate total time based on dependency count
        # Empirical: 445 deps → 26K packages → 41 min actual
        # Estimate ~25% higher so users are happy when it finishes early
        if len(dep_sboms) > 50:
            est_packages = len(dep_sboms) * 58  # avg packages per dep
            est_minutes = max(1, (est_packages * 18) // 10000)  # ~25% buffer
            click.echo(
                f"\n⏱️  Estimated total time: ~{est_minutes} minutes "
                f"(validation is the slowest step)"
            )

        click.echo("\n🔄 Merging SBOMs...")
        merger = SbomMerger()
        result = merger.merge_sboms(root_sbom, dep_sboms)

        click.echo(
            f"✅ Merge completed in {result.statistics.processing_time_seconds:.2f}s"
        )
        click.echo(f"   Total packages: {result.statistics.total_packages}")
        click.echo(
            f"   Duplicates removed: {result.statistics.duplicate_packages_removed}"
        )
        click.echo(f"   Total relationships: {result.statistics.total_relationships}")

        output_path = FileHandler.get_output_path(root_sbom, output_dir)

        # Serialize merged document to JSON
        serialized = SpdxParser.serialize_to_json(result.merged_document)

        # Validate BEFORE saving - if validation fails, don't create files
        click.echo("🔍 Validating merged SBOM against SPDX 2.3 specification...")

        def progress_callback(msg: str):
            """Display validation progress with carriage return for updates."""
            # Use carriage return to overwrite spinner lines
            if msg.startswith(("⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏")):
                click.echo(f"\r   {msg}", nl=False)
            else:
                click.echo(f"\r   {msg}                    ")

        validator = SpdxSpecValidator(progress_callback=progress_callback)
        validation_result = validator.validate_json_data(serialized)
        click.echo()  # New line after spinner

        if validation_result.warnings and verbose:
            click.echo(f"⚠️  {len(validation_result.warnings)} validation warnings")
            for warning in validation_result.warnings[:5]:
                click.echo(f"   ⚠️  {warning[:100]}")

        if not validation_result.is_valid:
            click.echo(
                f"\n❌ SPDX validation failed with "
                f"{len(validation_result.errors)} errors:"
            )
            for error in validation_result.errors[:10]:
                click.echo(f"   ❌ {error[:100]}")
            if len(validation_result.errors) > 10:
                click.echo(
                    f"   ... and {len(validation_result.errors) - 10} more errors"
                )
            click.echo("\n❌ Merged SBOM NOT saved due to validation errors.")
            sys.exit(1)

        click.echo(f"✅ SPDX validation passed ({validation_result.validator_used})")

        # Only save files if validation passed
        click.echo(f"\n💾 Saving merged SBOM to: {output_path}")
        FileHandler.save_merged_sbom(serialized, output_path)

        click.echo("📊 Generating merge report...")
        MergeReporter.generate_report(result, output_path)

        if result.statistics.validation_errors:
            click.echo(
                f"\n⚠️  {len(result.statistics.validation_errors)} "
                f"validation errors found"
            )
            for error in result.statistics.validation_errors:
                click.echo(f"   ❌ {error}")

        if result.statistics.validation_warnings:
            click.echo(
                f"\n⚠️  {len(result.statistics.validation_warnings)} "
                f"validation warnings found"
            )
            if verbose:
                for warning in result.statistics.validation_warnings:
                    click.echo(f"   ⚠️  {warning}")

        if push_to_github:
            if not github_owner or not github_repo:
                click.echo(
                    "\n❌ Error: --github-owner and --github-repo "
                    "required with --push-to-github"
                )
                sys.exit(1)

            click.echo(f"\n🔐 Loading GitHub credentials from: {key_file}")
            config = Config(str(key_file))

            if account:
                gh_account = config.get_account(account)
                if not gh_account:
                    click.echo(
                        f"❌ Error: Account '{account}' not found in " f"{key_file}"
                    )
                    sys.exit(1)
            else:
                gh_account = config.get_default_account()
                if not gh_account:
                    click.echo(f"❌ Error: No accounts found in {key_file}")
                    sys.exit(1)

            click.echo(f"✅ Using GitHub account: {gh_account.username}")

            click.echo(f"\n📤 Pushing to GitHub: {github_owner}/{github_repo}")
            client = GitHubClient(gh_account.token)

            try:
                client.upload_file_to_repo(
                    github_owner,
                    github_repo,
                    output_path,
                    github_path,
                    github_branch,
                    f"Add merged SBOM from {root_sbom.name}",
                )
                click.echo(
                    f"✅ Successfully pushed to "
                    f"{github_owner}/{github_repo}:{github_branch}"
                )
                click.echo(f"   Path: {github_path}")
            except Exception as e:
                click.echo(f"❌ Failed to push to GitHub: {e}")
                sys.exit(1)

        click.echo("\n" + "=" * 70)
        click.echo("✅ SBOM merge completed successfully!")
        click.echo("=" * 70)
        click.echo(f"\nMerged SBOM: {output_path}")
        report_path = output_path.parent / f"{output_path.stem}_merge_report.md"
        click.echo(f"Merge Report: {report_path}")

    except FileNotFoundError as e:
        click.echo(f"\n❌ Error: {e}")
        sys.exit(1)
    except ValueError as e:
        click.echo(f"\n❌ Error: {e}")
        sys.exit(1)
    except Exception as e:
        click.echo(f"\n❌ Unexpected error: {e}")
        if verbose:
            import traceback

            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
