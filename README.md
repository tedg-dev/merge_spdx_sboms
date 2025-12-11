# SPDX SBOM Merger

**Merge SPDX dependency SBOMs into a comprehensive root SBOM with complete relationship preservation**

[![CI/CD Pipeline](https://github.com/tedg-dev/merge_spdx_sboms/actions/workflows/ci.yml/badge.svg)](https://github.com/tedg-dev/merge_spdx_sboms/actions/workflows/ci.yml)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A production-ready Python application for merging SPDX Software Bill of Materials (SBOMs) from dependencies into a comprehensive root SBOM, maintaining complete relationship hierarchies and generating unique deterministic IDs.

---

## Features

✅ **Deterministic SPDX ID Generation** - Creates unique, reproducible IDs for all packages  
✅ **Hierarchical Relationship Merging** - Preserves complete transitive dependency graphs  
✅ **SPDX 2.3 Validation** - Ensures spec compliance with detailed validation reports  
✅ **Package Deduplication** - Automatically removes duplicate packages across SBOMs  
✅ **GitHub Integration** - Optional push to GitHub repositories  
✅ **Comprehensive Reports** - Detailed merge statistics and validation results  
✅ **96%+ Test Coverage** - Thoroughly tested with pytest  
✅ **CI/CD Pipeline** - GitHub Actions with automated testing and security scanning  

---

## Quick Start

### Setup Environment

```bash
# Setup and install
./setup_environment.sh

# Setup and run tests
./setup_environment.sh --test

# Setup and view coverage
./setup_environment.sh --coverage
```

### Basic Usage

```bash
# Merge SBOMs from dependencies directory
python -m sbom_merger.cli \
  --dependencies-dir /path/to/sboms/project_name/dependencies \
  --verbose

# Merge and push to GitHub
python -m sbom_merger.cli \
  --dependencies-dir /path/to/sboms/project_name/dependencies \
  --push-to-github \
  --github-owner tedg-dev \
  --github-repo my-project \
  --account tedg-dev
```

---

## How It Works

### Input Structure

The tool expects the directory structure created by `fetch_sbom`:

```
sboms/
  sbom_export_2025-12-10_09.37.18/
    CiscoSecurityServices_corona-sdk/
      CiscoSecurityServices_corona-sdk_root.json  ← Root SBOM
      dependencies/                                ← Input directory
        psf_requests_main.json
        pytest-dev_pytest_main.json
        ...
```

### Merge Process

1. **Discover Files** - Automatically finds root SBOM and all dependency SBOMs
2. **Parse & Validate** - Validates SPDX 2.3 format and version compatibility
3. **Generate New IDs** - Creates deterministic SPDXRef IDs for uniqueness
4. **Merge Packages** - Combines all packages (no deduplication)
5. **Preserve Relationships** - Maintains hierarchical DEPENDS_ON relationships
6. **Create Report** - Generates detailed merge statistics

### SPDX ID Generation

Uses industry best practice: **deterministic ID generation**

```python
SPDXRef-{ecosystem}-{sanitized-name}-{hash}

Examples:
- SPDXRef-pypi-requests-abc123
- SPDXRef-npm-lodash-def456
- SPDXRef-githubactions-actions-checkout-789xyz
```

**Why deterministic?**
- Guarantees uniqueness within merged document
- Reproducible across merges
- No collision risk from different source SBOMs

### Relationship Strategy

**Hierarchical with full transitive dependency preservation:**

```
Root SBOM (DESCRIBES)
  └─ Main Project
      ├─ DEPENDS_ON → pytest
      │   └─ DEPENDS_ON → pytest-cov
      │       └─ DEPENDS_ON → coverage
      └─ DEPENDS_ON → requests
          └─ DEPENDS_ON → urllib3
```

All relationships from dependency SBOMs are preserved, creating a complete dependency graph.

---

## Installation

### Prerequisites

- Python 3.12 or later
- Git

### Using setup_environment.sh (Recommended)

```bash
git clone https://github.com/tedg-dev/merge_spdx_sboms.git
cd merge_spdx_sboms
./setup_environment.sh
source venv/bin/activate
```

### Manual Installation

```bash
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

---

## Configuration

### GitHub Authentication

Create `keys.json` for GitHub push functionality:

```json
{
  "accounts": [
    {
      "username": "your-github-username",
      "token": "ghp_yourPersonalAccessToken"
    },
    {
      "username": "your-work-account",
      "token": "ghp_yourWorkAccessToken"
    }
  ]
}
```

**Token Requirements:**
- **Classic PAT**: `repo` scope
- **Fine-grained PAT**: Contents (Read/Write) permission

**Security:**
- Use `keys.sample.json` as template
- `keys.json` is gitignored by default
- Rotate tokens regularly

---

## Command-Line Interface

### Required Options

```bash
--dependencies-dir PATH    Path to dependencies directory
```

### Optional Options

```bash
--output-dir PATH          Output directory (default: same as root SBOM)
--key-file PATH            Path to keys.json (default: keys.json)
--account USERNAME         GitHub account from keys.json
--verbose                  Enable verbose output
```

### GitHub Push Options

```bash
--push-to-github           Push merged SBOM to GitHub
--github-owner OWNER       Repository owner (required with --push-to-github)
--github-repo REPO         Repository name (required with --push-to-github)
--github-path PATH         Target path in repo (default: sboms/merged_sbom.json)
--github-branch BRANCH     Target branch (default: main)
```

### Examples

**Basic merge:**
```bash
python -m sbom_merger.cli \
  --dependencies-dir ~/sboms/export/my-project/dependencies
```

**Verbose with custom output:**
```bash
python -m sbom_merger.cli \
  --dependencies-dir ~/sboms/export/my-project/dependencies \
  --output-dir ./output \
  --verbose
```

**Push to GitHub:**
```bash
python -m sbom_merger.cli \
  --dependencies-dir ~/sboms/export/my-project/dependencies \
  --push-to-github \
  --github-owner tedg-dev \
  --github-repo my-project \
  --github-branch main \
  --account tedg-dev \
  --verbose
```

---

## Output

### Merged SBOM

**Format:** SPDX 2.3 JSON  
**Location:** Same directory as root SBOM (or --output-dir)  
**Naming:** `{project}_merged.json`

```json
{
  "sbom": {
    "spdxVersion": "SPDX-2.3",
    "name": "Merged SBOM: com.github.owner/repo",
    "packages": [...],
    "relationships": [...]
  }
}
```

### Merge Report

**Format:** Markdown  
**Location:** `{merged_sbom}_merge_report.md`

**Contents:**
- Merge statistics (packages, relationships, processing time)
- Validation results (errors and warnings)
- Document details
- Package source breakdown

---

## Testing

### Run Tests

```bash
# All tests with coverage
./setup_environment.sh --test

# Manual testing
pytest --cov=src/sbom_merger --cov-report=term-missing -v

# Specific test file
pytest tests/test_merger.py -v

# With HTML coverage report
pytest --cov=src/sbom_merger --cov-report=html
```

### Coverage Requirements

- **Minimum:** 96% code coverage
- **Target:** 98%+ coverage
- Tests run automatically in CI/CD pipeline

---

## Architecture

### Project Structure

```
merge_spdx_sboms/
├── src/sbom_merger/
│   ├── domain/
│   │   └── models.py              # Data models
│   ├── services/
│   │   ├── merger.py              # Core merge logic
│   │   ├── parser.py              # SPDX parsing
│   │   ├── id_generator.py       # Deterministic ID generation
│   │   ├── validator.py           # SPDX validation
│   │   └── reporter.py            # Report generation
│   ├── infrastructure/
│   │   ├── config.py              # Configuration & auth
│   │   ├── file_handler.py       # File operations
│   │   └── github_client.py      # GitHub API
│   └── cli.py                     # Command-line interface
├── tests/                         # Comprehensive test suite
├── .github/workflows/             # CI/CD pipelines
└── setup_environment.sh           # Environment setup script
```

### Design Principles

- **SPDX 2.3 Spec Compliance** - Strict adherence to SPDX standards
- **Deterministic Operations** - Reproducible merges
- **No Data Loss** - All packages and relationships preserved
- **Validation First** - Validate before and after merge
- **Extensible Design** - Placeholder support for YAML, RDF formats

---

## CI/CD Pipeline

### Automated Testing

**On Push/PR:**
- ✅ Unit tests (Python 3.12)
- ✅ Code coverage (96%+ required)
- ✅ Linting (Black, Flake8, MyPy)
- ✅ Security scanning (Bandit, Safety)
- ✅ Package build verification

**On Release:**
- ✅ PyPI publishing
- ✅ Docker image build
- ✅ GitHub release creation

### GitHub Actions Workflows

- **ci.yml** - Test, lint, build on every push
- **release.yml** - Publish to PyPI on release
- **codeql.yml** - Security analysis (weekly + on push)

---

## Development

### Setup Development Environment

```bash
./setup_environment.sh
source venv/bin/activate
pip install -r requirements-dev.txt
```

### Code Quality Tools

```bash
# Format code
black src/ tests/

# Lint
flake8 src/ tests/

# Type checking
mypy src/sbom_merger

# Security scan
bandit -r src/
```

### Running Tests Locally

**Before committing:**
```bash
./setup_environment.sh --test
```

**Ensure:**
- All tests pass ✅
- Coverage ≥ 96% ✅
- No linting errors ✅

---

## Troubleshooting

### Common Issues

**"No root SBOM found"**
- Ensure path ends with `/dependencies`
- Root SBOM must match `*_root.json` pattern
- Check parent directory for root file

**"Multiple root SBOMs found"**
- Only one `*_root.json` file allowed
- Remove duplicate root SBOMs

**"Failed to push to GitHub"**
- Verify token has correct permissions
- Check repository exists
- Ensure branch name is correct

**"Validation errors"**
- All SBOMs must be SPDX-2.3 format
- Check SPDX version compatibility
- Review validation report for details

---

## Comparison with Alternatives

| Feature | merge-spdx-sboms | Manual Merge | Other Tools |
|---------|------------------|--------------|-------------|
| SPDX 2.3 Support | ✅ Full | ❌ Error-prone | ⚠️ Varies |
| Transitive Dependencies | ✅ Preserved | ❌ Lost | ⚠️ Limited |
| Deterministic IDs | ✅ Yes | ❌ No | ❌ No |
| Validation | ✅ Built-in | ❌ Manual | ⚠️ Basic |
| GitHub Integration | ✅ Native | ❌ Manual | ❌ No |
| Test Coverage | ✅ 96%+ | N/A | ⚠️ Unknown |

---

## Roadmap

### Future Enhancements

- [ ] SPDX 3.0 support (placeholder exists)
- [ ] YAML output format (placeholder exists)
- [ ] RDF output format (placeholder exists)
- [ ] Deduplication option (configurable)
- [ ] Multiple output formats simultaneously
- [ ] License compatibility checking
- [ ] Vulnerability correlation

---

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure 96%+ coverage maintained
5. Run `./setup_environment.sh --test`
6. Submit a pull request

---

## License

MIT License - see [LICENSE](LICENSE) file for details

---

## Documentation

- **[Architecture](docs/ARCHITECTURE.md)** - System design and component details
- **[Features](docs/FEATURES.md)** - Comprehensive feature documentation
- **[API Reference](docs/API.md)** - Python API and CLI documentation
- **[Testing Guide](docs/TESTING.md)** - Testing procedures and coverage
- **[GitHub Setup](docs/GITHUB_SETUP.md)** - Repository configuration and CI/CD
- **[Usage Examples](USAGE.md)** - Quick start examples and workflows

## Support

- **Issues**: [GitHub Issues](https://github.com/tedg-dev/merge_spdx_sboms/issues)
- **Documentation**: See `docs/` directory
- **CI/CD**: GitHub Actions workflows

---

## Acknowledgments

- SPDX Working Group for the SPDX specification
- Python spdx-tools library maintainers
- GitHub for SBOM API and infrastructure

---

**Built with ❤️ for secure software supply chains**
