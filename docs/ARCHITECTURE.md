# Architecture

## Overview

The SPDX SBOM Merger follows a clean architecture pattern with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────┐
│                     CLI Interface                        │
│                    (cli.py)                             │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│                    Services Layer                        │
│  ┌───────────┐  ┌──────────┐  ┌─────────────────────┐ │
│  │  Merger   │  │ Validator │  │  Reporter           │ │
│  │  Service  │  │          │  │                     │ │
│  └───────────┘  └──────────┘  └─────────────────────┘ │
│  ┌───────────┐  ┌──────────┐  ┌─────────────────────┐ │
│  │  Parser   │  │ ID Gen   │  │                     │ │
│  │           │  │          │  │                     │ │
│  └───────────┘  └──────────┘  └─────────────────────┘ │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│                 Infrastructure Layer                     │
│  ┌──────────────┐  ┌────────────┐  ┌────────────────┐ │
│  │ File Handler │  │   Config   │  │ GitHub Client  │ │
│  └──────────────┘  └────────────┘  └────────────────┘ │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│                     Domain Models                        │
│              (Data structures & types)                   │
└─────────────────────────────────────────────────────────┘
```

## Components

### Domain Layer (`domain/`)

**Purpose:** Core business entities and data structures

**Files:**
- `models.py` - Data classes for SPDX documents, packages, relationships, and merge results

**Design:**
- Immutable where possible
- No business logic, pure data structures
- Used across all layers

### Services Layer (`services/`)

**Purpose:** Core business logic and operations

#### Merger Service (`merger.py`)
- **Responsibility:** Orchestrates the entire merge process
- **Key Methods:**
  - `merge_sboms()` - Main entry point for merging
  - `_create_merged_document()` - Combines all SBOMs
  - `_find_main_package()` - Identifies root package
- **Flow:**
  1. Parse root SBOM
  2. Parse all dependency SBOMs
  3. Validate version compatibility
  4. Generate new unique IDs
  5. Merge packages and relationships
  6. Create merged document

#### Parser Service (`parser.py`)
- **Responsibility:** SPDX JSON parsing and serialization
- **Key Methods:**
  - `parse_sbom_file()` - Loads SPDX from file
  - `serialize_to_json()` - Converts to SPDX JSON
- **Features:**
  - Handles both wrapped (`{"sbom": {...}}`) and unwrapped formats
  - Preserves all SPDX fields
  - Tracks source file for provenance

#### ID Generator (`id_generator.py`)
- **Responsibility:** Deterministic SPDX ID generation
- **Key Methods:**
  - `generate_spdx_id()` - Creates unique IDs
  - `sanitize_name()` - Cleans package names
  - `extract_ecosystem()` - Identifies package type
  - `generate_hash()` - Creates 6-char hash
- **Format:** `SPDXRef-{ecosystem}-{name}-{hash}`
- **Guarantees:**
  - Uniqueness within document
  - Reproducibility across runs
  - No collision risk

#### Validator Service (`validator.py`)
- **Responsibility:** SPDX spec compliance validation
- **Key Methods:**
  - `validate_document()` - Single document validation
  - `validate_version_compatibility()` - Multi-document validation
- **Checks:**
  - SPDX version support (2.3)
  - Required fields presence
  - ID uniqueness
  - Relationship integrity
- **Output:** Lists of errors and warnings

#### Reporter Service (`reporter.py`)
- **Responsibility:** Generate merge reports
- **Key Methods:**
  - `generate_report()` - Creates markdown report
- **Content:**
  - Merge statistics
  - Validation results
  - Document details
  - Package source breakdown

### Infrastructure Layer (`infrastructure/`)

**Purpose:** External system interactions and cross-cutting concerns

#### File Handler (`file_handler.py`)
- **Responsibility:** File system operations
- **Key Methods:**
  - `discover_sbom_files()` - Finds root and dependency SBOMs
  - `save_merged_sbom()` - Writes merged SBOM
  - `get_output_path()` - Determines output location
- **Validation:**
  - Path must end with `/dependencies`
  - Exactly one root SBOM (`*_root.json`)
  - At least one dependency SBOM

#### Config (`config.py`)
- **Responsibility:** Configuration and authentication
- **Key Features:**
  - Multi-account GitHub authentication
  - SPDX version compatibility checks
  - Output format support
- **Format Support:**
  - Current: JSON
  - Future: YAML, RDF (placeholders)

#### GitHub Client (`github_client.py`)
- **Responsibility:** GitHub API interactions
- **Key Methods:**
  - `upload_file_to_repo()` - Push SBOM to GitHub
  - `update_repository_description()` - Set repo description
  - `create_release()` - Create GitHub release
- **Features:**
  - Token-based authentication
  - Automatic file updates (checks existing SHA)
  - Error handling with detailed messages

### CLI Layer (`cli.py`)

**Purpose:** Command-line interface

**Features:**
- Click-based argument parsing
- Verbose output mode
- GitHub push integration
- Comprehensive error handling

**Flow:**
1. Parse arguments
2. Discover SBOM files
3. Invoke merger service
4. Save results
5. Generate report
6. Optional: Push to GitHub

## Design Decisions

### 1. Deterministic ID Generation

**Why:** Industry best practice for SBOM merging
- Guarantees uniqueness within merged document
- Reproducible across runs
- No collision risk from different source documents

**Alternative Rejected:** Preserve original IDs
- High collision risk
- Violates SPDX uniqueness requirement

### 2. No Package Deduplication

**Why:** Complete dependency tracking
- Keeps all instances for full provenance
- Preserves version variations
- Supports security analysis

**Alternative Rejected:** Deduplicate by name+version
- Loses relationship context
- May hide supply chain complexities

### 3. Hierarchical Relationship Preservation

**Why:** Complete dependency graph
- Maintains transitive dependencies
- Enables security vulnerability tracing
- Supports compliance analysis

**Structure:**
```
Root → Dep1 → SubDep1
    → Dep2 → SubDep2
           → SubDep3
```

### 4. Validation-First Approach

**Why:** Prevent invalid merges
- Validates before merge
- Validates after merge
- Reports all issues with context

### 5. Extensible Output Format

**Current:** JSON only
**Future:** YAML, RDF (placeholders exist)
- Clean separation of serialization logic
- Easy to add new formats

## Data Flow

```
Input Files
    ↓
File Handler (discover)
    ↓
Parser (parse root & deps)
    ↓
Validator (check compatibility)
    ↓
Merger Service
    ├→ ID Generator (create unique IDs)
    ├→ Package merging
    └→ Relationship merging
    ↓
Validator (validate result)
    ↓
Parser (serialize)
    ↓
File Handler (save)
    ↓
Reporter (generate report)
    ↓
[Optional] GitHub Client (push)
    ↓
Output Files
```

## Testing Strategy

### Unit Tests
- Each service tested independently
- Mocked dependencies
- Edge cases covered

### Integration Tests
- End-to-end merge flows
- Real file operations (temp dirs)
- CLI invocation

### Coverage Requirements
- Minimum: 96%
- Target: 98%+
- Enforced in CI/CD

## Error Handling

### Validation Errors
- Stop merge process
- Report all issues
- Clear error messages

### File System Errors
- FileNotFoundError for missing files
- ValueError for invalid structure
- Detailed context in messages

### GitHub API Errors
- HTTP status code reporting
- API response details
- Token validation

## Performance Considerations

### Memory
- Streaming JSON parsing for large SBOMs
- Lazy loading where possible
- Efficient data structures

### Time
- Linear complexity for merging
- Parallel validation (where safe)
- Minimal redundant operations

## Security Considerations

### Credentials
- keys.json gitignored
- No hardcoded tokens
- Environment variable support

### Input Validation
- SPDX version checks
- Path traversal prevention
- JSON structure validation

### Dependencies
- Regular security scanning (Bandit)
- Dependency vulnerability checks (Safety)
- Minimal dependency footprint
