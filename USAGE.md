# Usage Guide

## Setting GitHub Repository Description

The application includes functionality to set a concise GitHub repository description via API.

### Using Python API

```python
from sbom_merger.infrastructure.github_client import GitHubClient

# Initialize client with your token
client = GitHubClient("ghp_your_token_here")

# Set repository description
client.update_repository_description(
    owner="tedg-dev",
    repo="merge_spdx_sboms",
    description="Merge SPDX dependency SBOMs into comprehensive root SBOM with full relationship preservation"
)
```

### Recommended Description

**Short version (for GitHub):**
```
Merge SPDX dependency SBOMs into comprehensive root SBOM with full relationship preservation
```

**Alternative short descriptions:**
- "SPDX SBOM merger with deterministic ID generation and hierarchical relationship preservation"
- "Merge SPDX SBOMs preserving transitive dependencies and complete relationship graphs"
- "Production-ready SPDX 2.3 SBOM merger for secure software supply chains"

## Quick Start Examples

### 1. Basic Merge

```bash
python -m sbom_merger.cli \
  --dependencies-dir ~/workspace/fetch_sbom/sboms/sbom_export_2025-12-10_09.37.18/CiscoSecurityServices_corona-sdk/dependencies \
  --verbose
```

### 2. Merge with Custom Output

```bash
python -m sbom_merger.cli \
  --dependencies-dir ~/workspace/fetch_sbom/sboms/sbom_export_2025-12-10_09.37.18/CiscoSecurityServices_corona-sdk/dependencies \
  --output-dir ./merged_sboms \
  --verbose
```

### 3. Merge and Push to GitHub

```bash
python -m sbom_merger.cli \
  --dependencies-dir ~/workspace/fetch_sbom/sboms/sbom_export_2025-12-10_09.37.18/CiscoSecurityServices_corona-sdk/dependencies \
  --push-to-github \
  --github-owner tedg-dev \
  --github-repo merge_spdx_sboms \
  --github-path sboms/merged_sbom.json \
  --account tedg-dev \
  --verbose
```

## Testing

### Run All Tests with Coverage

```bash
./setup_environment.sh --test
```

This will:
- Run all pytest tests
- Generate coverage report
- Fail if coverage < 96%
- Create HTML coverage report in `htmlcov/`

### View Coverage Report

```bash
./setup_environment.sh --coverage
```

Opens the HTML coverage report in your browser.

## Development Workflow

1. **Setup environment:**
   ```bash
   ./setup_environment.sh
   source venv/bin/activate
   ```

2. **Make changes to code**

3. **Run tests before committing:**
   ```bash
   ./setup_environment.sh --test
   ```

4. **Commit and push:**
   ```bash
   git add .
   git commit -m "Your commit message"
   git push origin main
   ```

5. **CI/CD automatically runs:**
   - Tests on Python 3.12
   - Linting (Black, Flake8, MyPy)
   - Security scanning (Bandit, Safety)
   - Build verification

## GitHub Repository Setup

### 1. Create Remote Repository

```bash
# Add remote
git remote add origin https://github.com/tedg-dev/merge_spdx_sboms.git

# Push to GitHub
git push -u origin main
```

### 2. Set Repository Description (via API)

```python
from sbom_merger.infrastructure.github_client import GitHubClient
from sbom_merger.infrastructure.config import Config

# Load credentials
config = Config("keys.json")
account = config.get_account("tedg-dev")

# Update description
client = GitHubClient(account.token)
client.update_repository_description(
    owner="tedg-dev",
    repo="merge_spdx_sboms",
    description="Merge SPDX dependency SBOMs into comprehensive root SBOM with full relationship preservation"
)
```

### 3. Configure Branch Protection

Go to: `https://github.com/tedg-dev/merge_spdx_sboms/settings/branches`

**Recommended settings:**
- ✅ Require pull request reviews before merging
- ✅ Require status checks to pass before merging
- ✅ Require branches to be up to date before merging
- ✅ Include administrators

## Troubleshooting

### Coverage Below 96%

If tests run but coverage is below 96%:

1. Check coverage report:
   ```bash
   pytest --cov=src/sbom_merger --cov-report=html
   open htmlcov/index.html
   ```

2. Identify uncovered lines

3. Add tests for uncovered code paths

### Import Errors

If you see import errors:

```bash
# Reinstall in development mode
pip install -e .

# Or use setup script
./setup_environment.sh
```

### GitHub API Errors

**403 Forbidden:**
- Check token permissions (needs `repo` scope)
- Verify token hasn't expired
- For SSO orgs, authorize token for org

**404 Not Found:**
- Verify repository exists
- Check owner and repo names
- Ensure token has access to repository
