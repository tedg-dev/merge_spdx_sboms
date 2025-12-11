# Features

## Core Features

### 1. Deterministic SPDX ID Generation

**Industry Best Practice Implementation**

Generates unique, reproducible SPDX IDs for all packages in the merged SBOM.

**Format:**
```
SPDXRef-{ecosystem}-{sanitized-name}-{hash}
```

**Examples:**
- `SPDXRef-pypi-requests-abc123`
- `SPDXRef-npm-lodash-def456`
- `SPDXRef-githubactions-actions-checkout-789xyz`

**Benefits:**
- ✅ Guarantees uniqueness within merged document
- ✅ Reproducible across multiple merges
- ✅ No collision risk from different source SBOMs
- ✅ Complies with SPDX 2.3 specification

**Algorithm:**
1. Extract ecosystem from package URL (purl)
2. Sanitize package name (remove special chars)
3. Generate 6-character hash from name+version
4. Combine into standard format

### 2. Hierarchical Relationship Merging

**Complete Transitive Dependency Preservation**

Maintains all dependency relationships from root and dependency SBOMs.

**Example Structure:**
```
Root SBOM (DESCRIBES main project)
  └─ Main Project
      ├─ DEPENDS_ON → pytest
      │   ├─ DEPENDS_ON → pytest-cov
      │   │   └─ DEPENDS_ON → coverage
      │   └─ DEPENDS_ON → pluggy
      └─ DEPENDS_ON → requests
          ├─ DEPENDS_ON → urllib3
          └─ DEPENDS_ON → certifi
```

**Benefits:**
- ✅ Complete dependency graph
- ✅ Enables vulnerability tracing
- ✅ Supports compliance analysis
- ✅ Reveals hidden dependencies

### 3. No Package Deduplication

**All Instances Preserved**

Keeps every package instance from all SBOMs, even duplicates.

**Why:**
- Different versions may exist in tree
- Preserves complete provenance
- Supports security analysis
- Maintains relationship context

**Example:**
```
Root: requests@2.31.0
Dep1: requests@2.30.0  ← Both kept
Dep2: urllib3@2.0.0
Dep3: urllib3@2.0.0    ← Both kept
```

### 4. SPDX 2.3 Validation

**Comprehensive Spec Compliance**

Validates before and after merge with detailed reporting.

**Validation Checks:**
- ✅ SPDX version compatibility
- ✅ Required field presence
- ✅ SPDX ID uniqueness
- ✅ Relationship integrity
- ✅ Document namespace format

**Output:**
- Errors (blocking issues)
- Warnings (non-blocking concerns)
- Detailed context for each issue

**Future Support:**
- SPDX 3.0 (placeholder exists)
- SPDX 3.0.1 (placeholder exists)

### 5. GitHub Integration

**Native GitHub API Support**

Push merged SBOMs directly to GitHub repositories.

**Capabilities:**
- ✅ Upload files to repository
- ✅ Update repository description
- ✅ Create releases
- ✅ Multi-account authentication

**Authentication:**
- Uses keys.json (same format as fetch_sbom)
- Supports multiple GitHub accounts
- Fine-grained or classic PAT tokens

**Example:**
```bash
python -m sbom_merger.cli \
  --dependencies-dir /path/to/dependencies \
  --push-to-github \
  --github-owner tedg-dev \
  --github-repo my-project \
  --account tedg-dev
```

### 6. Comprehensive Reporting

**Detailed Merge Statistics and Validation**

Generates markdown reports with complete merge information.

**Report Contents:**
- Merge statistics (packages, relationships, time)
- Validation results (errors and warnings)
- Document details (version, namespace, license)
- Package source breakdown
- Processing time

**Output Files:**
- `{project}_merged.json` - Merged SBOM
- `{project}_merged_merge_report.md` - Merge report

### 7. Command-Line Interface

**User-Friendly CLI with Rich Options**

Full-featured command-line interface with verbose mode.

**Required:**
```bash
--dependencies-dir PATH    # Path to dependencies directory
```

**Optional:**
```bash
--output-dir PATH          # Custom output location
--key-file PATH            # Custom keys.json path
--account USERNAME         # GitHub account to use
--verbose                  # Detailed output
--push-to-github           # Enable GitHub push
--github-owner OWNER       # Repository owner
--github-repo REPO         # Repository name
--github-path PATH         # Target path in repo
--github-branch BRANCH     # Target branch
```

### 8. Automated Testing

**96%+ Code Coverage Requirement**

Comprehensive test suite with enforced coverage.

**Test Types:**
- Unit tests (individual components)
- Integration tests (end-to-end flows)
- Edge case coverage
- Error path validation

**Running Tests:**
```bash
./setup_environment.sh --test
```

**Features:**
- Automatic virtual environment setup
- Dependency installation
- Coverage reporting (HTML + terminal)
- Fail on coverage < 96%

### 9. CI/CD Pipeline

**Best-Practice GitHub Actions Workflows**

Automated testing, security, and deployment.

**Workflows:**

**ci.yml** (On push/PR):
- ✅ Tests on Python 3.12
- ✅ Code coverage ≥ 96%
- ✅ Linting (Black, Flake8, MyPy)
- ✅ Security scanning (Bandit, Safety)
- ✅ Package build verification
- ✅ Integration tests

**release.yml** (On release):
- ✅ PyPI publishing
- ✅ Docker image build
- ✅ GitHub release assets

**codeql.yml** (Weekly + push):
- ✅ Security analysis
- ✅ Vulnerability detection

### 10. Environment Setup Script

**One-Command Environment Configuration**

Automated setup script for development and testing.

**Usage:**
```bash
# Setup only
./setup_environment.sh

# Setup and test
./setup_environment.sh --test

# Setup and view coverage
./setup_environment.sh --coverage

# Setup and run app
./setup_environment.sh --run
```

**Features:**
- ✅ Python version detection
- ✅ Virtual environment creation
- ✅ Dependency installation
- ✅ Package installation in dev mode
- ✅ Test execution with coverage
- ✅ HTML coverage report generation

## Advanced Features

### File Discovery

**Automatic SBOM Detection**

Intelligently discovers root and dependency SBOMs.

**Requirements:**
- Path must end with `/dependencies`
- Exactly one `*_root.json` in parent directory
- At least one JSON file in dependencies directory

**Example Structure:**
```
sboms/
  sbom_export_2025-12-10_09.37.18/
    project_name/
      project_name_root.json       ← Auto-detected
      dependencies/                ← Input path
        dep1.json
        dep2.json
```

### Output Flexibility

**Current and Future Format Support**

**Supported Now:**
- JSON (SPDX 2.3 format)

**Planned (Placeholders Exist):**
- YAML output
- RDF output
- Multiple formats simultaneously

**Configuration:**
```python
Config.SUPPORTED_OUTPUT_FORMATS = ["json"]
Config.FUTURE_OUTPUT_FORMATS = ["yaml", "rdf"]
```

### Version Compatibility

**SPDX Version Management**

**Currently Supported:**
- SPDX 2.3 (full support)

**Future Versions (Placeholders):**
- SPDX 3.0
- SPDX 3.0.1

**Behavior:**
- Blocks merge if unsupported version found
- Warns if future version detected
- Clear error messages with version info

### Multi-Account GitHub Support

**Flexible Authentication**

Supports multiple GitHub accounts in single keys.json.

**Format:**
```json
{
  "accounts": [
    {
      "username": "personal-account",
      "token": "ghp_token1"
    },
    {
      "username": "work-account",
      "token": "ghp_token2"
    }
  ]
}
```

**Usage:**
```bash
--account personal-account    # Use specific account
# or omit to use first account
```

### Repository Description Management

**GitHub API Integration**

Set repository description via API.

**Usage:**
```python
from sbom_merger.infrastructure.github_client import GitHubClient

client = GitHubClient(token)
client.update_repository_description(
    owner="tedg-dev",
    repo="merge_spdx_sboms",
    description="Merge SPDX dependency SBOMs into comprehensive root SBOM"
)
```

## Feature Roadmap

### Planned Enhancements

**Short Term:**
- [ ] YAML output format
- [ ] RDF output format
- [ ] Configurable deduplication

**Medium Term:**
- [ ] SPDX 3.0 support
- [ ] License compatibility checking
- [ ] Vulnerability correlation

**Long Term:**
- [ ] Web UI for merge visualization
- [ ] Real-time validation feedback
- [ ] Batch processing mode
- [ ] Custom validation rules
