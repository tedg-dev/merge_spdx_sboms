# Versioning Guide

This project follows [Semantic Versioning 2.0.0](https://semver.org/) (SemVer) for version identification.

## Version Format

```
MAJOR.MINOR.PATCH
```

- **MAJOR**: Incompatible API changes
- **MINOR**: New functionality (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

## Version Source

The single source of truth for the version is the `VERSION` file in the project root:

```
/VERSION
```

This file is read by:
- `pyproject.toml` for package builds
- `src/sbom_merger/__version__.py` for runtime version access
- GitHub Actions release workflow for tag validation

## Automatic Version Bumping

The **patch version is automatically incremented** when a PR is merged to `main`.

### How It Works

1. A PR is merged to `main`
2. The `version-bump.yml` workflow triggers
3. The patch version increments: `1.0.5` → `1.0.6`
4. The workflow commits the updated VERSION file
5. Commit message includes `[skip ci]` to prevent infinite loops

### Example

```
PR #15 merged → VERSION bumped from 1.0.14 to 1.0.15
PR #16 merged → VERSION bumped from 1.0.15 to 1.0.16
```

### Manual Version Updates

For **major** or **minor** version bumps (breaking changes or new features), manually update the VERSION file:

```bash
echo "2.0.0" > VERSION
git add VERSION
git commit -m "chore: bump major version to 2.0.0"
git push origin main
```

## Creating a Release

### 1. Verify VERSION File

The VERSION file should already be at the correct patch version from PR merges.
For major/minor releases, update it manually first.

### 2. Create an Annotated Tag

Use annotated tags (not lightweight) for releases:

```bash
VERSION=$(cat VERSION)
git tag -a v$VERSION -m "Release v$VERSION: Brief description of changes"
git push origin v$VERSION
```

### 3. Automated Release Process

Pushing a tag matching `v*.*.*` triggers the release workflow which:

1. **Validates** the VERSION file matches the tag
2. **Builds** Python wheel and source distribution
3. **Publishes** to PyPI
4. **Generates** SBOM using Syft (SPDX 2.3 JSON format)
5. **Creates** GitHub Release with:
   - Release notes
   - Distribution files
   - SBOM artifact
6. **Builds** and pushes Docker image to GHCR

## Version in Code

Access the version programmatically:

```python
from sbom_merger.__version__ import __version__

print(f"Running version: {__version__}")
```

## Pre-release Versions

For pre-release versions, use suffixes:

- Alpha: `1.1.0-alpha.1`
- Beta: `1.1.0-beta.1`
- Release Candidate: `1.1.0-rc.1`

## SBOM Version Tracking

Every release includes an SBOM (`sbom.spdx.json`) attached to the GitHub Release. The SBOM includes:

- All dependencies with their versions
- Package metadata
- License information
- SPDX 2.3 compliant format

## Best Practices

1. **Never reuse tags** - Each version should be unique
2. **Keep VERSION file in sync** - Always update before tagging
3. **Use descriptive tag messages** - Include summary of changes
4. **Test before release** - Ensure all tests pass before tagging
5. **Document breaking changes** - Use MAJOR version bump and document in release notes

## Manual Release (workflow_dispatch)

For manual releases without pushing a tag:

1. Go to Actions → Release Pipeline
2. Click "Run workflow"
3. Enter the version number (e.g., `1.1.0`)
4. The workflow will create the release and tag

## Verifying a Release

Check the installed version:

```bash
pip show merge-spdx-sboms | grep Version
```

Or in Python:

```python
import sbom_merger
print(sbom_merger.__version__)
```
