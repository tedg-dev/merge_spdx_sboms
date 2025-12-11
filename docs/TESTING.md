# Testing Guide

## Overview

The SPDX SBOM Merger has comprehensive test coverage with a 96%+ requirement enforced in CI/CD.

## Running Tests

### Quick Start

```bash
# Setup environment and run all tests
./setup_environment.sh --test
```

This will:
1. Create virtual environment (if needed)
2. Install all dependencies
3. Run pytest with coverage
4. Fail if coverage < 96%
5. Generate HTML coverage report

### Manual Testing

```bash
# Activate environment
source venv/bin/activate

# Run all tests
pytest -v

# Run with coverage
pytest --cov=src/sbom_merger --cov-report=term-missing -v

# Run with HTML coverage report
pytest --cov=src/sbom_merger --cov-report=html -v

# Fail if coverage < 96%
pytest --cov=src/sbom_merger --cov-fail-under=96 -v
```

### Specific Test Files

```bash
# Test merger service
pytest tests/test_merger.py -v

# Test ID generator
pytest tests/test_id_generator.py -v

# Test validator
pytest tests/test_validator.py -v

# Test with keyword filter
pytest -k "test_merge" -v
```

## Test Structure

### Test Files

```
tests/
├── __init__.py
├── conftest.py              # Shared fixtures
├── test_merger.py           # Merger service tests
├── test_id_generator.py     # ID generation tests
├── test_validator.py        # Validation tests
├── test_parser.py           # Parser tests
├── test_reporter.py         # Reporter tests
├── test_file_handler.py     # File handler tests
└── test_config.py           # Config tests
```

### Test Fixtures

**conftest.py** provides shared fixtures:

```python
@pytest.fixture
def sample_root_sbom():
    # Returns sample root SBOM data
    
@pytest.fixture
def sample_dependency_sbom():
    # Returns sample dependency SBOM data
    
@pytest.fixture
def temp_sbom_dir():
    # Creates temporary directory with SBOM files
```

## Coverage Requirements

### Minimum Coverage: 96%

**Enforced in:**
- Local testing (`./setup_environment.sh --test`)
- CI/CD pipeline (GitHub Actions)

**Check coverage:**
```bash
pytest --cov=src/sbom_merger --cov-report=term-missing
```

**View HTML report:**
```bash
pytest --cov=src/sbom_merger --cov-report=html
open htmlcov/index.html
```

### Coverage Report Example

```
Name                                          Stmts   Miss  Cover   Missing
---------------------------------------------------------------------------
src/sbom_merger/__init__.py                       1      0   100%
src/sbom_merger/cli.py                          120      8    93%   45-48, 67
src/sbom_merger/domain/models.py                 42      0   100%
src/sbom_merger/infrastructure/config.py         56      2    96%   88-89
src/sbom_merger/infrastructure/file_handler.py   48      1    98%   67
src/sbom_merger/infrastructure/github_client.py  52      5    90%   71-75 (target: 96%)
src/sbom_merger/services/id_generator.py         35      0   100%
src/sbom_merger/services/merger.py              105      4    96%   123-126
src/sbom_merger/services/parser.py               67      2    97%   45-46
src/sbom_merger/services/reporter.py             58      3    95%   78-80
src/sbom_merger/services/validator.py            78      4    95%   56-59
---------------------------------------------------------------------------
TOTAL                                           662     29    96%
```

## Test Categories

### Unit Tests

Test individual components in isolation.

**Example:**
```python
def test_generate_spdx_id():
    refs = [{
        "referenceType": "purl",
        "referenceLocator": "pkg:pypi/requests@2.31.0"
    }]
    
    spdx_id = SpdxIdGenerator.generate_spdx_id(
        "requests",
        "2.31.0",
        refs
    )
    
    assert spdx_id.startswith("SPDXRef-pypi-")
    assert "requests" in spdx_id
```

### Integration Tests

Test complete workflows end-to-end.

**Example:**
```python
def test_merge_sboms(temp_sbom_dir):
    root_sbom, dep_sboms = FileHandler.discover_sbom_files(temp_sbom_dir)
    
    merger = SbomMerger()
    result = merger.merge_sboms(root_sbom, dep_sboms)
    
    assert result.merged_document is not None
    assert result.statistics.total_packages > 0
```

### Edge Case Tests

Test boundary conditions and error scenarios.

**Example:**
```python
def test_discover_sbom_files_not_dependencies_dir():
    with tempfile.TemporaryDirectory() as tmpdir:
        wrong_dir = Path(tmpdir) / "wrong_name"
        wrong_dir.mkdir()
        
        with pytest.raises(ValueError, match="must end with 'dependencies'"):
            FileHandler.discover_sbom_files(wrong_dir)
```

## Writing Tests

### Best Practices

1. **Use fixtures** for common test data
2. **Test one thing** per test function
3. **Use descriptive names** (e.g., `test_merge_creates_unique_ids`)
4. **Test error paths** as well as success paths
5. **Use pytest markers** for slow tests
6. **Mock external dependencies** (file I/O, network calls)

### Example Test

```python
import pytest
from pathlib import Path
from sbom_merger.services.merger import SbomMerger

def test_merge_validates_version_compatibility(temp_sbom_dir):
    """Test that merge validates SPDX version compatibility"""
    root_sbom, dep_sboms = discover_files(temp_sbom_dir)
    
    merger = SbomMerger()
    result = merger.merge_sboms(root_sbom, dep_sboms)
    
    # Should have no validation errors for compatible versions
    assert len(result.statistics.validation_errors) == 0
    
def test_merge_fails_on_incompatible_versions():
    """Test that merge fails on incompatible SPDX versions"""
    # Setup test data with incompatible versions
    ...
    
    merger = SbomMerger()
    
    with pytest.raises(ValueError, match="validation errors"):
        merger.merge_sboms(root_sbom, dep_sboms)
```

## Continuous Integration

### GitHub Actions

Tests run automatically on:
- Every push to main/develop
- Every pull request
- Manual workflow dispatch

**Workflow:** `.github/workflows/ci.yml`

**Steps:**
1. Checkout code
2. Set up Python 3.12
3. Install dependencies
4. Run tests with coverage
5. Upload coverage report
6. Fail if coverage < 96%

### Local Pre-Commit

Before committing:

```bash
# Run tests
./setup_environment.sh --test

# Format code
black src/ tests/

# Lint
flake8 src/ tests/

# Type check
mypy src/sbom_merger
```

## Debugging Tests

### Verbose Output

```bash
# Show print statements
pytest -v -s

# Show full diff on failures
pytest -v --tb=long

# Stop on first failure
pytest -x
```

### Debugging in IDE

**VS Code:**
1. Set breakpoint in test file
2. Run "Python: Debug Tests" from command palette

**PyCharm:**
1. Right-click test function
2. Select "Debug 'pytest in test_file.py'"

### Coverage Gaps

**Find uncovered lines:**
```bash
pytest --cov=src/sbom_merger --cov-report=term-missing
```

**View in HTML:**
```bash
pytest --cov=src/sbom_merger --cov-report=html
open htmlcov/index.html
```

Red lines indicate uncovered code.

## Performance Testing

### Timing Tests

```bash
# Show slowest tests
pytest --durations=10
```

### Profiling

```bash
# Profile test execution
pytest --profile

# Profile with output
pytest --profile-svg
```

## Test Data

### Sample SBOMs

Located in `tests/conftest.py`:
- `sample_root_sbom` - Minimal valid root SBOM
- `sample_dependency_sbom` - Minimal valid dependency SBOM
- `temp_sbom_dir` - Temporary directory with files

### Creating Test Data

```python
import tempfile
from pathlib import Path
import json

def create_test_sbom(tmpdir, filename, data):
    """Helper to create test SBOM file"""
    path = Path(tmpdir) / filename
    with open(path, 'w') as f:
        json.dump(data, f)
    return path
```

## Troubleshooting

### Common Issues

**Import Errors:**
```bash
# Reinstall in development mode
pip install -e .
```

**Coverage Not Calculated:**
```bash
# Ensure you're testing the installed package
pytest --cov=src/sbom_merger
```

**Tests Pass Locally, Fail in CI:**
- Check Python version (CI uses 3.12)
- Check for environment-specific paths
- Review CI logs for details

### Getting Help

1. Check test output for detailed error messages
2. Review HTML coverage report for gaps
3. Run tests with `-v -s` for verbose output
4. Check GitHub Actions logs for CI failures
