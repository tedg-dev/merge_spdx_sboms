from sbom_merger.services.id_generator import SpdxIdGenerator


class TestSanitizeName:
    """Tests for SPDXID name sanitization per SPDX 2.3 spec."""

    def test_preserves_valid_characters(self):
        """Hyphens, dots, and alphanumerics are allowed."""
        assert SpdxIdGenerator.sanitize_name("test-package") == "test-package"
        assert SpdxIdGenerator.sanitize_name("package.name") == "package.name"
        assert SpdxIdGenerator.sanitize_name("Package123") == "Package123"

    def test_replaces_special_characters(self):
        """Special characters like @ and / are replaced with hyphens."""
        assert SpdxIdGenerator.sanitize_name("@scope/package") == "scope-package"

    def test_replaces_underscores_with_hyphens(self):
        """SPDX 2.3 spec: underscores are NOT allowed in SPDXID idstring."""
        assert SpdxIdGenerator.sanitize_name("package_name") == "package-name"
        assert SpdxIdGenerator.sanitize_name("my_long_name") == "my-long-name"
        assert SpdxIdGenerator.sanitize_name("__leading") == "leading"

    def test_collapses_multiple_hyphens(self):
        """Multiple consecutive hyphens are collapsed to one."""
        assert SpdxIdGenerator.sanitize_name("a--b") == "a-b"
        assert SpdxIdGenerator.sanitize_name("a___b") == "a-b"

    def test_strips_leading_trailing_hyphens(self):
        """Leading and trailing hyphens are removed."""
        assert SpdxIdGenerator.sanitize_name("-package-") == "package"
        assert SpdxIdGenerator.sanitize_name("--test--") == "test"


class TestSpdxIdValidation:
    """Tests for SPDXID format validation per SPDX 2.3 spec."""

    def test_valid_spdx_ids(self):
        """Valid SPDXIDs should pass validation."""
        assert SpdxIdGenerator.is_valid_spdx_id("SPDXRef-DOCUMENT")
        assert SpdxIdGenerator.is_valid_spdx_id("SPDXRef-Package-1")
        assert SpdxIdGenerator.is_valid_spdx_id("SPDXRef-pypi-requests-abc123")
        assert SpdxIdGenerator.is_valid_spdx_id("SPDXRef-a.b.c")
        assert SpdxIdGenerator.is_valid_spdx_id("SPDXRef-test-1.2.3")

    def test_invalid_spdx_id_with_underscore(self):
        """SPDX 2.3 spec: underscores are NOT allowed."""
        assert not SpdxIdGenerator.is_valid_spdx_id("SPDXRef-package_name")
        assert not SpdxIdGenerator.is_valid_spdx_id("SPDXRef-my_pkg_123")

    def test_invalid_spdx_id_missing_prefix(self):
        """SPDXID must start with 'SPDXRef-'."""
        assert not SpdxIdGenerator.is_valid_spdx_id("Package-1")
        assert not SpdxIdGenerator.is_valid_spdx_id("spdxref-test")

    def test_invalid_spdx_id_empty_idstring(self):
        """SPDXID must have non-empty idstring after prefix."""
        assert not SpdxIdGenerator.is_valid_spdx_id("SPDXRef-")
        assert not SpdxIdGenerator.is_valid_spdx_id("")

    def test_validate_spdx_id_returns_errors(self):
        """validate_spdx_id should return descriptive error messages."""
        errors = SpdxIdGenerator.validate_spdx_id("SPDXRef-invalid_id")
        assert len(errors) > 0
        assert any("underscore" in e.lower() for e in errors)

        errors = SpdxIdGenerator.validate_spdx_id("BadPrefix-test")
        assert len(errors) > 0
        assert any("SPDXRef-" in e for e in errors)

    def test_validate_spdx_id_empty_returns_error(self):
        """Empty SPDXID should return error."""
        errors = SpdxIdGenerator.validate_spdx_id("")
        assert len(errors) > 0
        assert any("empty" in e.lower() for e in errors)

    def test_generated_spdx_ids_are_valid(self):
        """All generated SPDXIDs should pass validation."""
        refs = [
            {"referenceType": "purl", "referenceLocator": "pkg:pypi/requests@2.31.0"}
        ]

        # Test with various package names including underscores
        test_names = [
            "requests",
            "my_package",
            "some-pkg",
            "@scope/package",
            "pkg_with_underscores_123",
        ]

        for name in test_names:
            spdx_id = SpdxIdGenerator.generate_spdx_id(name, "1.0.0", refs)
            assert SpdxIdGenerator.is_valid_spdx_id(spdx_id), (
                f"Generated SPDXID '{spdx_id}' for '{name}' is invalid"
            )


def test_extract_ecosystem():
    refs = [{"referenceType": "purl", "referenceLocator": "pkg:pypi/requests"}]
    assert SpdxIdGenerator.extract_ecosystem(refs) == "pypi"

    refs = [{"referenceType": "purl", "referenceLocator": "pkg:npm/lodash"}]
    assert SpdxIdGenerator.extract_ecosystem(refs) == "npm"

    assert SpdxIdGenerator.extract_ecosystem([]) == "unknown"


def test_generate_hash():
    hash1 = SpdxIdGenerator.generate_hash("requests", "2.31.0")
    hash2 = SpdxIdGenerator.generate_hash("requests", "2.31.0")
    hash3 = SpdxIdGenerator.generate_hash("requests", "2.30.0")

    assert len(hash1) == 6
    assert hash1 == hash2
    assert hash1 != hash3


def test_generate_spdx_id():
    refs = [{"referenceType": "purl", "referenceLocator": "pkg:pypi/requests@2.31.0"}]

    spdx_id = SpdxIdGenerator.generate_spdx_id("requests", "2.31.0", refs)

    assert spdx_id.startswith("SPDXRef-pypi-")
    assert "requests" in spdx_id
    assert len(spdx_id.split("-")[-1]) == 6


def test_generate_document_namespace():
    namespace = SpdxIdGenerator.generate_document_namespace("test-sbom")

    assert namespace.startswith("https://spdx.org/spdxdocs/merged-sbom/")
    assert len(namespace) > 50
