# GitHub Repository Setup Guide

## Creating the Repository

### 1. Create Empty Repository

Go to: https://github.com/new

**Settings:**
- **Owner:** tedg-dev
- **Repository name:** merge_spdx_sboms
- **Description:** (Set via API after creation)
- **Visibility:** Public or Private
- **DO NOT initialize with README, .gitignore, or license** (already exists locally)

### 2. Push Local Repository

```bash
cd /Users/tedg/workspace/merge_spdx_sboms

# Add remote
git remote add origin https://github.com/tedg-dev/merge_spdx_sboms.git

# Push to GitHub
git push -u origin main
```

### 3. Set Repository Description (via API)

```python
from sbom_merger.infrastructure.github_client import GitHubClient

client = GitHubClient("your_github_token")
client.update_repository_description(
    owner="tedg-dev",
    repo="merge_spdx_sboms",
    description="Merge SPDX dependency SBOMs into comprehensive root SBOM with full relationship preservation"
)
```

## Required Repository Settings

### General Settings

**Go to:** `Settings` → `General`

**Repository name:** `merge_spdx_sboms`

**Description:** 
```
Merge SPDX dependency SBOMs into comprehensive root SBOM with full relationship preservation
```

**Topics (add these):**
- `spdx`
- `sbom`
- `security`
- `supply-chain`
- `python`
- `software-composition-analysis`
- `dependencies`

**Features (enable these):**
- ✅ Issues
- ✅ Projects
- ✅ Preserve this repository (optional)
- ✅ Sponsorships (optional)
- ✅ Discussions (optional)
- ❌ Wikis (use docs/ instead)

**Pull Requests:**
- ✅ Allow merge commits
- ✅ Allow squash merging
- ✅ Allow rebase merging
- ✅ Always suggest updating pull request branches
- ✅ Automatically delete head branches

### Branch Protection Rules

**Go to:** `Settings` → `Branches` → `Add rule`

**Branch name pattern:** `main`

**Protect matching branches:**

✅ **Require a pull request before merging**
- Required approvals: 1 (for team projects)
- Dismiss stale pull request approvals when new commits are pushed
- Require review from Code Owners (if CODEOWNERS file added)

✅ **Require status checks to pass before merging**
- Require branches to be up to date before merging
- **Status checks required:**
  - `test (3.12)` - Test suite must pass
  - `lint` - Code quality checks must pass
  - `security` - Security scans must pass
  - `build` - Package build must succeed

✅ **Require conversation resolution before merging**

✅ **Require signed commits** (optional but recommended)

✅ **Include administrators**

✅ **Restrict who can push to matching branches** (optional)

✅ **Allow force pushes**
- ❌ Disable (recommended for main branch)

✅ **Allow deletions**
- ❌ Disable (protect main branch)

### Actions Settings

**Go to:** `Settings` → `Actions` → `General`

**Actions permissions:**
- ✅ Allow all actions and reusable workflows

**Workflow permissions:**
- ✅ Read and write permissions
- ✅ Allow GitHub Actions to create and approve pull requests

**Artifact and log retention:**
- Set to: `90 days` (default)

**Fork pull request workflows:**
- ✅ Require approval for all outside collaborators

### Secrets and Variables

**Go to:** `Settings` → `Secrets and variables` → `Actions`

**Repository secrets (for releases):**

Add these when ready to publish:

1. **PYPI_API_TOKEN**
   - Get from: https://pypi.org/manage/account/token/
   - Scope: Entire account or specific project
   - Use for publishing to PyPI

2. **TEST_PYPI_API_TOKEN**
   - Get from: https://test.pypi.org/manage/account/token/
   - Use for testing release pipeline

**Note:** GITHUB_TOKEN is automatically available, no need to add.

### Code Security and Analysis

**Go to:** `Settings` → `Code security and analysis`

**Dependency graph:**
- ✅ Enable (automatically enabled for public repos)

**Dependabot alerts:**
- ✅ Enable

**Dependabot security updates:**
- ✅ Enable

**Dependabot version updates:**
- ✅ Enable
- Create `.github/dependabot.yml`:

```yaml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 10
    
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
```

**Code scanning:**
- ✅ CodeQL analysis (already configured in `.github/workflows/codeql.yml`)

**Secret scanning:**
- ✅ Enable (automatic for public repos)
- ✅ Push protection (prevents committing secrets)

### Pages (Optional)

**Go to:** `Settings` → `Pages`

If you want to host documentation:

**Source:** 
- Deploy from a branch: `gh-pages`
- Or use GitHub Actions

### Environments

**Go to:** `Settings` → `Environments`

**Create environment:** `release`

**Environment protection rules:**
- ✅ Required reviewers: Add yourself
- ✅ Wait timer: 0 minutes
- ✅ Deployment branches: Only `main`

**Environment secrets:**
- Add `PYPI_API_TOKEN` here instead of repository secrets for extra security

## Best Practices Settings Summary

### Critical Settings

1. ✅ **Branch protection on `main`**
   - Require PR reviews
   - Require status checks
   - No force push
   - No deletion

2. ✅ **Required CI checks**
   - Tests must pass
   - Linting must pass
   - Security scans must pass
   - 96%+ coverage required

3. ✅ **Security features**
   - Dependabot alerts
   - CodeQL analysis
   - Secret scanning
   - Push protection

4. ✅ **Actions permissions**
   - Read/write access for CI
   - Artifact retention configured

### Recommended Settings

1. ✅ **Signed commits** (optional but good practice)
2. ✅ **Code owners** (create CODEOWNERS file)
3. ✅ **Release environment** with approval gate
4. ✅ **Dependabot version updates**
5. ✅ **Auto-delete head branches** after merge

### Optional Settings

1. ⚪ **Discussions** for community
2. ⚪ **Projects** for task tracking
3. ⚪ **Pages** for documentation hosting
4. ⚪ **Sponsorships** if accepting funding

## Initial Setup Checklist

After pushing to GitHub:

- [ ] Enable branch protection on `main`
- [ ] Verify CI workflows run successfully
- [ ] Check test coverage report in Actions
- [ ] Enable Dependabot alerts
- [ ] Set up CodeQL (automatic from workflow)
- [ ] Add repository topics
- [ ] Set repository description (via API)
- [ ] Create first release (optional)
- [ ] Add CODEOWNERS file (optional)
- [ ] Configure dependabot.yml
- [ ] Add PYPI tokens when ready to publish

## Monitoring CI/CD

### Check Workflow Status

**Go to:** `Actions` tab

You should see:
- ✅ CI/CD Pipeline (on every push)
- ✅ CodeQL Security Analysis (weekly)
- ⚪ Release Pipeline (on releases only)

### First Push Expectations

After `git push -u origin main`:

1. **CI/CD Pipeline triggers:**
   - Checkout code ✅
   - Set up Python 3.12 ✅
   - Install dependencies ✅
   - Run tests with coverage ✅
   - Code coverage ≥ 96% ✅
   - Linting (Black, Flake8) ✅
   - Type checking (MyPy) ✅
   - Security scanning (Bandit) ✅
   - Build package ✅

2. **Expected duration:** 3-5 minutes

3. **Success indicators:**
   - Green checkmark on commit
   - All jobs passed
   - Coverage badge shows 96%+

### Troubleshooting CI Failures

**If tests fail:**
- Review test logs in Actions tab
- Run locally: `./setup_environment.sh --test`
- Fix issues and push again

**If coverage fails:**
- Check coverage report in Actions artifacts
- Add tests for uncovered code
- Verify coverage ≥ 96%

**If linting fails:**
- Run locally: `black src/ tests/`
- Run: `flake8 src/ tests/`
- Fix issues and push

## Badge Setup

Add to README.md (already included):

```markdown
[![CI/CD Pipeline](https://github.com/tedg-dev/merge_spdx_sboms/actions/workflows/ci.yml/badge.svg)](https://github.com/tedg-dev/merge_spdx_sboms/actions/workflows/ci.yml)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
```

Badges show:
- CI/CD status
- Python version requirement
- License type

## Security Considerations

### Secrets Management

**Never commit:**
- `keys.json` (gitignored)
- API tokens
- Private keys
- Passwords

**Use GitHub Secrets for:**
- PyPI API tokens
- Release credentials
- Third-party API keys

### Access Control

**Repository access:**
- Owner: Full access
- Maintainers: Push, but not delete
- Contributors: Fork and PR only

**Token scopes:**
- Minimum required permissions
- Regular rotation
- Separate tokens for different purposes

### Dependency Security

**Automated checks:**
- Dependabot alerts for vulnerabilities
- CodeQL for code security issues
- Bandit for Python security patterns
- Safety for known vulnerabilities

**Response plan:**
1. Review Dependabot alerts
2. Update vulnerable dependencies
3. Run tests to verify
4. Create PR with security label
5. Merge after review

## Release Management

### Creating a Release

1. **Tag version:**
   ```bash
   git tag -a v1.0.0 -m "Release v1.0.0"
   git push origin v1.0.0
   ```

2. **Create release on GitHub:**
   - Go to: `Releases` → `Create a new release`
   - Tag: `v1.0.0`
   - Title: `v1.0.0 - Initial Release`
   - Description: Release notes
   - Attach: Distribution files (automatic from workflow)

3. **Release workflow triggers:**
   - Build package
   - Publish to PyPI (if configured)
   - Create Docker image
   - Attach artifacts to release

### Semantic Versioning

Follow semver: `MAJOR.MINOR.PATCH`

- **MAJOR:** Breaking changes
- **MINOR:** New features (backward compatible)
- **PATCH:** Bug fixes

Examples:
- `1.0.0` - Initial stable release
- `1.1.0` - Added YAML output format
- `1.1.1` - Fixed validation bug
- `2.0.0` - SPDX 3.0 support (breaking)
