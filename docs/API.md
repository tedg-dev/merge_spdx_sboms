# API Reference

## Python API

### Merger Service

#### `SbomMerger`

Main service for merging SPDX SBOMs.

```python
from sbom_merger.services.merger import SbomMerger
from pathlib import Path

merger = SbomMerger()
result = merger.merge_sboms(
    root_sbom_path=Path("root.json"),
    dependency_sbom_paths=[Path("dep1.json"), Path("dep2.json")]
)

print(f"Total packages: {result.statistics.total_packages}")
print(f"Total relationships: {result.statistics.total_relationships}")
```

**Methods:**

- `merge_sboms(root_sbom_path: Path, dependency_sbom_paths: List[Path]) -> MergeResult`
  - Merges root and dependency SBOMs
  - Returns MergeResult with merged document and statistics
  - Raises ValueError on validation errors

### Parser Service

#### `SpdxParser`

Parse and serialize SPDX JSON documents.

```python
from sbom_merger.services.parser import SpdxParser
from pathlib import Path

# Parse
doc = SpdxParser.parse_sbom_file(Path("sbom.json"))

# Serialize
json_data = SpdxParser.serialize_to_json(doc)
```

**Methods:**

- `parse_sbom_file(file_path: Path) -> SpdxDocument`
  - Parses SPDX JSON file
  - Handles wrapped and unwrapped formats
  - Returns SpdxDocument object

- `serialize_to_json(document: SpdxDocument) -> Dict[str, Any]`
  - Converts SpdxDocument to JSON dict
  - Returns wrapped format: `{"sbom": {...}}`

### ID Generator

#### `SpdxIdGenerator`

Generate deterministic SPDX IDs.

```python
from sbom_merger.services.id_generator import SpdxIdGenerator

# Generate ID
spdx_id = SpdxIdGenerator.generate_spdx_id(
    name="requests",
    version="2.31.0",
    external_refs=[{
        "referenceType": "purl",
        "referenceLocator": "pkg:pypi/requests@2.31.0"
    }]
)
# Returns: "SPDXRef-pypi-requests-abc123"

# Generate namespace
namespace = SpdxIdGenerator.generate_document_namespace("my-sbom")
# Returns: "https://spdx.org/spdxdocs/merged-sbom/{uuid}"
```

**Methods:**

- `generate_spdx_id(name: str, version: Optional[str], external_refs: Optional[list]) -> str`
- `sanitize_name(name: str) -> str`
- `extract_ecosystem(external_refs: list) -> str`
- `generate_hash(name: str, version: Optional[str]) -> str`
- `generate_document_namespace(base_name: str) -> str`

### Validator Service

#### `SpdxValidator`

Validate SPDX documents against specification.

```python
from sbom_merger.services.validator import SpdxValidator

# Validate single document
errors, warnings = SpdxValidator.validate_document(document)

if errors:
    print("Validation failed:")
    for error in errors:
        print(f"  - {error}")

# Validate compatibility
errors, warnings = SpdxValidator.validate_version_compatibility([doc1, doc2])
```

**Methods:**

- `validate_document(document: SpdxDocument) -> Tuple[List[str], List[str]]`
  - Returns (errors, warnings)
  - Errors are blocking issues
  - Warnings are non-blocking concerns

- `validate_version_compatibility(documents: List[SpdxDocument]) -> Tuple[List[str], List[str]]`
  - Validates multiple documents for compatibility
  - Returns (errors, warnings)

### Reporter Service

#### `MergeReporter`

Generate merge reports.

```python
from sbom_merger.services.reporter import MergeReporter
from pathlib import Path

# Generate report
report = MergeReporter.generate_report(
    result=merge_result,
    output_path=Path("output/merged.json")
)

print(report)  # Markdown formatted report
```

**Methods:**

- `generate_report(result: MergeResult, output_path: Optional[Path]) -> str`
  - Generates markdown report
  - Optionally saves to file
  - Returns report content as string

### File Handler

#### `FileHandler`

File system operations.

```python
from sbom_merger.infrastructure.file_handler import FileHandler
from pathlib import Path

# Discover SBOMs
root_sbom, dep_sboms = FileHandler.discover_sbom_files(
    Path("/path/to/dependencies")
)

# Save merged SBOM
FileHandler.save_merged_sbom(
    sbom_data={"sbom": {...}},
    output_path=Path("output/merged.json")
)

# Get output path
output_path = FileHandler.get_output_path(
    root_sbom_path=Path("root.json"),
    output_dir=Path("output")
)
```

**Methods:**

- `discover_sbom_files(dependencies_dir: Path) -> Tuple[Path, List[Path]]`
  - Returns (root_sbom_path, dependency_sbom_paths)
  - Raises FileNotFoundError if files not found
  - Raises ValueError if invalid structure

- `save_merged_sbom(sbom_data: dict, output_path: Path) -> None`
- `get_output_path(root_sbom_path: Path, output_dir: Optional[Path]) -> Path`

### GitHub Client

#### `GitHubClient`

GitHub API interactions.

```python
from sbom_merger.infrastructure.github_client import GitHubClient
from pathlib import Path

client = GitHubClient(token="ghp_yourtoken")

# Upload file
client.upload_file_to_repo(
    owner="tedg-dev",
    repo="my-project",
    file_path=Path("merged.json"),
    target_path="sboms/merged.json",
    branch="main",
    commit_message="Add merged SBOM"
)

# Update repo description
client.update_repository_description(
    owner="tedg-dev",
    repo="my-project",
    description="My project description"
)

# Create release
release = client.create_release(
    owner="tedg-dev",
    repo="my-project",
    tag_name="v1.0.0",
    name="Release v1.0.0",
    body="Release notes"
)
```

**Methods:**

- `upload_file_to_repo(owner, repo, file_path, target_path, branch, commit_message) -> bool`
- `update_repository_description(owner, repo, description) -> bool`
- `create_release(owner, repo, tag_name, name, body) -> dict`

### Config

#### `Config`

Configuration and authentication management.

```python
from sbom_merger.infrastructure.config import Config

config = Config(key_file="keys.json")

# Get account
account = config.get_account("tedg-dev")
print(account.username, account.token)

# Get default account
default_account = config.get_default_account()

# Check version support
is_supported = Config.is_supported_spdx_version("SPDX-2.3")  # True
is_supported = Config.is_supported_spdx_version("SPDX-3.0")  # False

# Check format support
is_supported = Config.is_supported_output_format("json")  # True
is_supported = Config.is_supported_output_format("yaml")  # False
```

**Methods:**

- `get_account(username: str) -> Optional[GitHubAccount]`
- `get_default_account() -> Optional[GitHubAccount]`
- `is_supported_spdx_version(version: str) -> bool` (static)
- `is_supported_output_format(fmt: str) -> bool` (static)

## Domain Models

### SpdxDocument

```python
@dataclass
class SpdxDocument:
    spdx_version: str
    data_license: str
    spdx_id: str
    name: str
    document_namespace: str
    creation_info: Dict[str, Any]
    packages: List[SpdxPackage] = field(default_factory=list)
    relationships: List[SpdxRelationship] = field(default_factory=list)
    comment: Optional[str] = None
    source_file: Optional[str] = None
```

### SpdxPackage

```python
@dataclass
class SpdxPackage:
    name: str
    spdx_id: str
    download_location: str = "NOASSERTION"
    files_analyzed: bool = False
    version_info: Optional[str] = None
    license_concluded: Optional[str] = None
    copyright_text: Optional[str] = None
    external_refs: List[Dict[str, str]] = field(default_factory=list)
    source_sbom: Optional[str] = None
```

### SpdxRelationship

```python
@dataclass
class SpdxRelationship:
    spdx_element_id: str
    related_spdx_element: str
    relationship_type: str
    source_sbom: Optional[str] = None
```

### MergeResult

```python
@dataclass
class MergeResult:
    merged_document: SpdxDocument
    statistics: MergeStatistics
    output_path: Optional[str] = None
```

### MergeStatistics

```python
@dataclass
class MergeStatistics:
    total_sboms_processed: int = 0
    root_packages_count: int = 0
    dependency_packages_count: int = 0
    total_packages: int = 0
    total_relationships: int = 0
    duplicate_packages_kept: int = 0
    processing_time_seconds: float = 0.0
    validation_errors: List[str] = field(default_factory=list)
    validation_warnings: List[str] = field(default_factory=list)
```

## CLI Usage

### Command Line Interface

```bash
python -m sbom_merger.cli --help
```

**Options:**

```
Required:
  --dependencies-dir PATH    Path to dependencies directory

Optional:
  --output-dir PATH          Output directory (default: same as root)
  --key-file PATH            Path to keys.json (default: keys.json)
  --account USERNAME         GitHub account from keys.json
  --verbose                  Enable verbose output

GitHub Push:
  --push-to-github           Push merged SBOM to GitHub
  --github-owner OWNER       Repository owner (required with --push-to-github)
  --github-repo REPO         Repository name (required with --push-to-github)
  --github-path PATH         Target path in repo (default: sboms/merged_sbom.json)
  --github-branch BRANCH     Target branch (default: main)
```

**Examples:**

```bash
# Basic merge
python -m sbom_merger.cli \
  --dependencies-dir /path/to/dependencies

# With verbose output
python -m sbom_merger.cli \
  --dependencies-dir /path/to/dependencies \
  --verbose

# Push to GitHub
python -m sbom_merger.cli \
  --dependencies-dir /path/to/dependencies \
  --push-to-github \
  --github-owner tedg-dev \
  --github-repo my-project \
  --account tedg-dev
```

## Environment Setup

### setup_environment.sh

```bash
# Setup only
./setup_environment.sh

# Setup and test
./setup_environment.sh --test

# Setup and view coverage
./setup_environment.sh --coverage

# Setup and run
./setup_environment.sh --run
```

## Error Handling

### Exceptions

**FileNotFoundError:**
- Raised when dependencies directory or root SBOM not found
- Contains detailed path information

**ValueError:**
- Raised on validation errors
- Contains list of all validation issues
- Raised on invalid directory structure

**Exception (GitHub):**
- Raised on GitHub API errors
- Contains HTTP status code and response text

### Example Error Handling

```python
from sbom_merger.services.merger import SbomMerger
from pathlib import Path

try:
    merger = SbomMerger()
    result = merger.merge_sboms(root, deps)
except FileNotFoundError as e:
    print(f"File not found: {e}")
except ValueError as e:
    print(f"Validation error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```
