"""Tests for SPDX specification validator using spdx-tools."""

import json
import tempfile
from pathlib import Path

from sbom_merger.services.spdx_spec_validator import (
    SpdxSpecValidator,
    ValidationResult,
    validate_spdx_output,
)


class TestSpdxSpecValidator:
    """Tests for the SpdxSpecValidator class."""

    def test_check_spdx_tools_available(self):
        """spdx-tools should be available in test environment."""
        validator = SpdxSpecValidator()
        assert validator._spdx_tools_available is True

    def test_validate_valid_spdx_json(self):
        """Valid SPDX JSON should pass validation."""
        validator = SpdxSpecValidator()

        valid_spdx = {
            "spdxVersion": "SPDX-2.3",
            "dataLicense": "CC0-1.0",
            "SPDXID": "SPDXRef-DOCUMENT",
            "name": "test-document",
            "documentNamespace": "https://example.com/test",
            "creationInfo": {
                "created": "2025-01-01T00:00:00Z",
                "creators": ["Tool: test"],
            },
            "packages": [
                {
                    "SPDXID": "SPDXRef-Package-1",
                    "name": "test-package",
                    "downloadLocation": "NOASSERTION",
                    "filesAnalyzed": False,
                }
            ],
        }

        result = validator.validate_json_data(valid_spdx)
        assert result.spdx_version == "SPDX-2.3"
        assert result.validator_used == "spdx-tools + custom"

    def test_validate_invalid_spdxid_with_underscore(self):
        """SPDXID with underscore should fail validation."""
        validator = SpdxSpecValidator()

        invalid_spdx = {
            "spdxVersion": "SPDX-2.3",
            "dataLicense": "CC0-1.0",
            "SPDXID": "SPDXRef-DOCUMENT",
            "name": "test",
            "documentNamespace": "https://example.com/test",
            "creationInfo": {
                "created": "2025-01-01T00:00:00Z",
                "creators": ["Tool: test"],
            },
            "packages": [
                {
                    "SPDXID": "SPDXRef-invalid_underscore",
                    "name": "test-pkg",
                    "downloadLocation": "NOASSERTION",
                    "filesAnalyzed": False,
                }
            ],
        }

        result = validator.validate_json_data(invalid_spdx)
        assert result.is_valid is False
        assert any("underscore" in e.lower() for e in result.errors)

    def test_validate_missing_required_fields(self):
        """Missing required fields should be detected."""
        validator = SpdxSpecValidator()

        incomplete_spdx = {
            "spdxVersion": "SPDX-2.3",
            "SPDXID": "SPDXRef-DOCUMENT",
        }

        result = validator.validate_json_data(incomplete_spdx)
        assert result.is_valid is False

    def test_validate_json_file_not_found(self):
        """Non-existent file should return error."""
        validator = SpdxSpecValidator()
        result = validator.validate_json_file(Path("/nonexistent/file.json"))

        assert result.is_valid is False
        assert any("not found" in e.lower() for e in result.errors)
        assert result.validator_used == "file_check"

    def test_validate_json_file_invalid_json(self):
        """Invalid JSON file should return error."""
        validator = SpdxSpecValidator()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write("{ invalid json }")
            temp_path = Path(f.name)

        try:
            result = validator.validate_json_file(temp_path)
            assert result.is_valid is False
            assert any("invalid json" in e.lower() for e in result.errors)
            assert result.validator_used == "json_parser"
        finally:
            temp_path.unlink(missing_ok=True)

    def test_validate_json_file_valid_spdx(self):
        """Valid SPDX JSON file should pass validation."""
        validator = SpdxSpecValidator()

        valid_spdx = {
            "spdxVersion": "SPDX-2.3",
            "dataLicense": "CC0-1.0",
            "SPDXID": "SPDXRef-DOCUMENT",
            "name": "test-document",
            "documentNamespace": "https://example.com/test",
            "creationInfo": {
                "created": "2025-01-01T00:00:00Z",
                "creators": ["Tool: test"],
            },
            "packages": [
                {
                    "SPDXID": "SPDXRef-Package-1",
                    "name": "test-package",
                    "downloadLocation": "NOASSERTION",
                    "filesAnalyzed": False,
                }
            ],
        }

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".spdx.json", delete=False
        ) as f:
            json.dump(valid_spdx, f)
            temp_path = Path(f.name)

        try:
            result = validator.validate_json_file(temp_path)
            assert result.spdx_version == "SPDX-2.3"
        finally:
            temp_path.unlink(missing_ok=True)

    def test_validate_all_spdx_ids_document(self):
        """Document SPDXID should be validated."""
        validator = SpdxSpecValidator()

        spdx_data = {
            "SPDXID": "SPDXRef-invalid_doc",
            "packages": [],
            "relationships": [],
        }

        errors = validator._validate_all_spdx_ids(spdx_data)
        assert len(errors) > 0
        assert any("Document" in e for e in errors)

    def test_validate_all_spdx_ids_packages(self):
        """Package SPDXIDs should be validated."""
        validator = SpdxSpecValidator()

        spdx_data = {
            "SPDXID": "SPDXRef-DOCUMENT",
            "packages": [
                {"SPDXID": "SPDXRef-valid-1", "name": "valid"},
                {"SPDXID": "SPDXRef-invalid_pkg", "name": "invalid"},
            ],
            "relationships": [],
        }

        errors = validator._validate_all_spdx_ids(spdx_data)
        assert len(errors) > 0
        assert any("invalid" in e.lower() and "Package" in e for e in errors)

    def test_validate_all_spdx_ids_relationships(self):
        """Relationship SPDXIDs should be validated."""
        validator = SpdxSpecValidator()

        spdx_data = {
            "SPDXID": "SPDXRef-DOCUMENT",
            "packages": [],
            "relationships": [
                {
                    "spdxElementId": "SPDXRef-bad_element",
                    "relatedSpdxElement": "SPDXRef-bad_related",
                    "relationshipType": "DESCRIBES",
                }
            ],
        }

        errors = validator._validate_all_spdx_ids(spdx_data)
        assert len(errors) >= 2


class TestBasicValidation:
    """Tests for basic validation fallback."""

    def test_basic_validation_missing_fields(self):
        """Basic validation should detect missing required fields."""
        validator = SpdxSpecValidator()

        incomplete = {"spdxVersion": "SPDX-2.3"}
        result = validator._basic_validation(incomplete)

        assert result.is_valid is False
        assert any("SPDXID" in e for e in result.errors)
        assert any("name" in e for e in result.errors)

    def test_basic_validation_unsupported_version(self):
        """Basic validation should flag unsupported versions."""
        validator = SpdxSpecValidator()

        data = {
            "spdxVersion": "SPDX-1.0",
            "SPDXID": "SPDXRef-DOCUMENT",
            "name": "test",
            "dataLicense": "CC0-1.0",
            "documentNamespace": "https://test.com",
            "creationInfo": {},
        }

        result = validator._basic_validation(data)
        assert any("Unsupported" in e for e in result.errors)

    def test_basic_validation_future_version_warning(self):
        """Basic validation should warn about future versions."""
        validator = SpdxSpecValidator()

        data = {
            "spdxVersion": "SPDX-3.0",
            "SPDXID": "SPDXRef-DOCUMENT",
            "name": "test",
            "dataLicense": "CC0-1.0",
            "documentNamespace": "https://test.com",
            "creationInfo": {},
        }

        result = validator._basic_validation(data)
        assert any("not fully supported" in w for w in result.warnings)

    def test_basic_validation_package_missing_fields(self):
        """Basic validation should check package required fields."""
        validator = SpdxSpecValidator()

        data = {
            "spdxVersion": "SPDX-2.3",
            "SPDXID": "SPDXRef-DOCUMENT",
            "name": "test",
            "dataLicense": "CC0-1.0",
            "documentNamespace": "https://test.com",
            "creationInfo": {},
            "packages": [
                {"name": "pkg1"},
                {"SPDXID": "SPDXRef-pkg2"},
            ],
        }

        result = validator._basic_validation(data)
        assert any("missing SPDXID" in e for e in result.errors)
        assert any("missing name" in e for e in result.errors)


class TestValidateSpdxOutput:
    """Tests for the convenience function."""

    def test_validate_spdx_output_valid_file(self):
        """validate_spdx_output should work with valid files."""
        valid_spdx = {
            "spdxVersion": "SPDX-2.3",
            "dataLicense": "CC0-1.0",
            "SPDXID": "SPDXRef-DOCUMENT",
            "name": "test",
            "documentNamespace": "https://test.com/test",
            "creationInfo": {
                "created": "2025-01-01T00:00:00Z",
                "creators": ["Tool: test"],
            },
            "packages": [
                {
                    "SPDXID": "SPDXRef-pkg",
                    "name": "test",
                    "downloadLocation": "NOASSERTION",
                    "filesAnalyzed": False,
                }
            ],
        }

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".spdx.json", delete=False
        ) as f:
            json.dump(valid_spdx, f)
            temp_path = Path(f.name)

        try:
            result = validate_spdx_output(temp_path)
            assert isinstance(result, ValidationResult)
            assert result.spdx_version == "SPDX-2.3"
        finally:
            temp_path.unlink(missing_ok=True)

    def test_validate_spdx_output_nonexistent_file(self):
        """validate_spdx_output should handle missing files."""
        result = validate_spdx_output(Path("/does/not/exist.json"))
        assert result.is_valid is False


class TestValidationResult:
    """Tests for ValidationResult dataclass."""

    def test_validation_result_creation(self):
        """ValidationResult should be creatable with all fields."""
        result = ValidationResult(
            is_valid=True,
            errors=[],
            warnings=["test warning"],
            spdx_version="SPDX-2.3",
            validator_used="test",
        )

        assert result.is_valid is True
        assert len(result.errors) == 0
        assert len(result.warnings) == 1
        assert result.spdx_version == "SPDX-2.3"
        assert result.validator_used == "test"


class TestFallbackValidation:
    """Tests for fallback when spdx-tools is unavailable."""

    def test_fallback_to_basic_when_spdx_tools_unavailable(self):
        """When spdx-tools unavailable, should use basic validation."""
        validator = SpdxSpecValidator()
        # Temporarily disable spdx-tools
        original_value = validator._spdx_tools_available
        validator._spdx_tools_available = False

        try:
            data = {
                "spdxVersion": "SPDX-2.3",
                "SPDXID": "SPDXRef-DOCUMENT",
                "name": "test",
                "dataLicense": "CC0-1.0",
                "documentNamespace": "https://test.com",
                "creationInfo": {},
            }
            result = validator.validate_json_data(data)
            assert result.validator_used == "basic + custom"
            assert any("spdx-tools library not available" in w for w in result.warnings)
        finally:
            validator._spdx_tools_available = original_value


class TestProgressCallback:
    """Tests for progress callback functionality."""

    def test_progress_callback_is_called(self):
        """Progress callback should be called during validation."""
        messages = []

        def callback(msg):
            messages.append(msg)

        validator = SpdxSpecValidator(progress_callback=callback)

        data = {
            "spdxVersion": "SPDX-2.3",
            "dataLicense": "CC0-1.0",
            "SPDXID": "SPDXRef-DOCUMENT",
            "name": "test",
            "documentNamespace": "https://test.com",
            "creationInfo": {
                "created": "2025-01-01T00:00:00Z",
                "creators": ["Tool: test"],
            },
            "packages": [
                {
                    "SPDXID": "SPDXRef-pkg",
                    "name": "test",
                    "downloadLocation": "NOASSERTION",
                    "filesAnalyzed": False,
                }
            ],
        }

        validator.validate_json_data(data)
        assert len(messages) > 0
        assert any("package" in m.lower() for m in messages)

    def test_progress_callback_large_sbom_estimate(self):
        """Large SBOMs should show time estimate in progress."""
        messages = []

        def callback(msg):
            messages.append(msg)

        validator = SpdxSpecValidator(progress_callback=callback)

        # Create SBOM with >1000 packages to trigger estimate message
        packages = []
        for i in range(1500):
            packages.append(
                {
                    "SPDXID": f"SPDXRef-pkg-{i}",
                    "name": f"package-{i}",
                    "downloadLocation": "NOASSERTION",
                    "filesAnalyzed": False,
                }
            )

        data = {
            "spdxVersion": "SPDX-2.3",
            "dataLicense": "CC0-1.0",
            "SPDXID": "SPDXRef-DOCUMENT",
            "name": "test",
            "documentNamespace": "https://test.com",
            "creationInfo": {
                "created": "2025-01-01T00:00:00Z",
                "creators": ["Tool: test"],
            },
            "packages": packages,
        }

        validator.validate_json_data(data)
        # Should have message about estimated time for large SBOMs
        assert any("may take" in m for m in messages)
        # 1500 packages * 12 / 10000 = 1.8 -> 1 minute estimate
        assert any("~1 minutes" in m or "~2 minutes" in m for m in messages)

    def test_no_callback_does_not_error(self):
        """Validator without callback should not error."""
        validator = SpdxSpecValidator()  # No callback

        data = {
            "spdxVersion": "SPDX-2.3",
            "dataLicense": "CC0-1.0",
            "SPDXID": "SPDXRef-DOCUMENT",
            "name": "test",
            "documentNamespace": "https://test.com",
            "creationInfo": {
                "created": "2025-01-01T00:00:00Z",
                "creators": ["Tool: test"],
            },
            "packages": [],
        }

        # Should not raise
        result = validator.validate_json_data(data)
        assert result.spdx_version == "SPDX-2.3"


class TestSpdxToolsErrorHandling:
    """Tests for spdx-tools error handling paths."""

    def test_spdx_tools_validation_with_error_messages(self):
        """Test that spdx-tools error messages are captured."""
        validator = SpdxSpecValidator()

        # Create document that will have spdx-tools errors (invalid SPDXID)
        data = {
            "spdxVersion": "SPDX-2.3",
            "dataLicense": "CC0-1.0",
            "SPDXID": "SPDXRef-DOCUMENT",
            "name": "test",
            "documentNamespace": "https://test.com",
            "creationInfo": {
                "created": "2025-01-01T00:00:00Z",
                "creators": ["Tool: test"],
            },
            "packages": [
                {
                    "SPDXID": "SPDXRef-invalid_pkg",
                    "name": "test",
                    "downloadLocation": "NOASSERTION",
                    "filesAnalyzed": False,
                }
            ],
        }

        result = validator._validate_with_spdx_tools(data)
        # Should have errors about underscore
        assert len(result.errors) > 0

    def test_spdx_tools_parsing_error_handling(self):
        """Test that parsing errors are handled gracefully."""
        validator = SpdxSpecValidator()

        # Create incomplete document that causes parsing error
        data = {
            "spdxVersion": "SPDX-2.3",
            "SPDXID": "SPDXRef-DOCUMENT",
        }

        result = validator._validate_with_spdx_tools(data)
        assert result.is_valid is False
        assert any("parsing" in e.lower() for e in result.errors)

    def test_spdx_tools_value_error_handling(self):
        """Test that ValueError is handled gracefully."""
        from unittest.mock import patch

        validator = SpdxSpecValidator()

        data = {
            "spdxVersion": "SPDX-2.3",
            "SPDXID": "SPDXRef-DOCUMENT",
        }

        with patch(
            "spdx_tools.spdx.parser.parse_anything.parse_file",
            side_effect=ValueError("test value error"),
        ):
            result = validator._validate_with_spdx_tools(data)
            assert result.is_valid is False
            assert any("validation error" in e.lower() for e in result.errors)

    def test_spdx_tools_generic_exception_handling(self):
        """Test that generic Exception is handled gracefully."""
        from unittest.mock import patch

        validator = SpdxSpecValidator()

        data = {
            "spdxVersion": "SPDX-2.3",
            "SPDXID": "SPDXRef-DOCUMENT",
        }

        with patch(
            "spdx_tools.spdx.parser.parse_anything.parse_file",
            side_effect=RuntimeError("unexpected error"),
        ):
            result = validator._validate_with_spdx_tools(data)
            assert result.is_valid is False
            assert any("validation error" in e.lower() for e in result.errors)
