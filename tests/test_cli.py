from click.testing import CliRunner
from sbom_merger.cli import main
import tempfile
from pathlib import Path


def test_cli_help():
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "dependencies-dir" in result.output


def test_cli_missing_required_arg():
    runner = CliRunner()
    result = runner.invoke(main, [])
    assert result.exit_code != 0


def test_cli_basic_merge(temp_sbom_dir):
    runner = CliRunner()
    result = runner.invoke(
        main,
        ["--dependencies-dir", str(temp_sbom_dir), "--verbose"],
        catch_exceptions=False,
    )

    if result.exit_code != 0:
        print(result.output)
        print(result.exception)

    assert result.exit_code == 0
    assert "Merge completed" in result.output


def test_cli_with_output_dir(temp_sbom_dir):
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as tmpdir:
        output_dir = Path(tmpdir) / "output"

        result = runner.invoke(
            main,
            ["--dependencies-dir", str(temp_sbom_dir), "--output-dir", str(output_dir)],
            catch_exceptions=False,
        )

        assert result.exit_code == 0
        assert output_dir.exists()


def test_cli_invalid_dependencies_dir():
    runner = CliRunner()
    result = runner.invoke(
        main, ["--dependencies-dir", "/nonexistent/path/dependencies"]
    )
    assert result.exit_code != 0
    assert "Error" in result.output


def test_cli_shows_time_estimate_for_large_sbom_count(
    sample_root_sbom, sample_dependency_sbom
):
    """Test that time estimate is shown when >50 dependency SBOMs."""
    import json
    import tempfile
    from pathlib import Path

    with tempfile.TemporaryDirectory() as tmpdir:
        base_path = Path(tmpdir)
        project_dir = base_path / "test_user_test_repo"
        deps_dir = project_dir / "dependencies"
        deps_dir.mkdir(parents=True)

        # Create root SBOM
        root_path = project_dir / "test_user_test_repo_root.json"
        with open(root_path, "w") as f:
            json.dump(sample_root_sbom, f)

        # Create 55 dependency SBOMs (>50 to trigger estimate)
        for i in range(55):
            dep_sbom = {
                "sbom": {
                    "spdxVersion": "SPDX-2.3",
                    "dataLicense": "CC0-1.0",
                    "SPDXID": "SPDXRef-DOCUMENT",
                    "name": f"dep-{i}",
                    "documentNamespace": f"https://example.com/dep-{i}",
                    "creationInfo": {
                        "creators": ["Tool: test"],
                        "created": "2025-01-01T00:00:00Z",
                    },
                    "packages": [
                        {
                            "name": f"package-{i}",
                            "SPDXID": f"SPDXRef-pkg-{i}",
                            "downloadLocation": "NOASSERTION",
                            "filesAnalyzed": False,
                        }
                    ],
                    "relationships": [],
                }
            }
            dep_path = deps_dir / f"dep_{i}.json"
            with open(dep_path, "w") as f:
                json.dump(dep_sbom, f)

        runner = CliRunner()
        result = runner.invoke(
            main,
            ["--dependencies-dir", str(deps_dir), "--verbose"],
            catch_exceptions=False,
        )

        # Should show time estimate for >50 deps
        assert "Estimated total time" in result.output
        assert "minutes" in result.output
