import pytest
from sbom_merger.services.validator import SpdxValidator
from sbom_merger.domain.models import SpdxDocument, SpdxPackage


def test_validate_document_success():
    doc = SpdxDocument(
        spdx_version="SPDX-2.3",
        data_license="CC0-1.0",
        spdx_id="SPDXRef-DOCUMENT",
        name="test",
        document_namespace="https://test.com/test",
        creation_info={"created": "2025-12-11T00:00:00Z"},
        packages=[
            SpdxPackage(
                name="test-package",
                spdx_id="SPDXRef-test-1"
            )
        ]
    )

    errors, warnings = SpdxValidator.validate_document(doc)
    assert len(errors) == 0


def test_validate_unsupported_version():
    doc = SpdxDocument(
        spdx_version="SPDX-3.0",
        data_license="CC0-1.0",
        spdx_id="SPDXRef-DOCUMENT",
        name="test",
        document_namespace="https://test.com/test",
        creation_info={"created": "2025-12-11T00:00:00Z"}
    )

    errors, warnings = SpdxValidator.validate_document(doc)
    assert len(warnings) > 0


def test_validate_duplicate_spdx_ids():
    doc = SpdxDocument(
        spdx_version="SPDX-2.3",
        data_license="CC0-1.0",
        spdx_id="SPDXRef-DOCUMENT",
        name="test",
        document_namespace="https://test.com/test",
        creation_info={"created": "2025-12-11T00:00:00Z"},
        packages=[
            SpdxPackage(name="pkg1", spdx_id="SPDXRef-test-1"),
            SpdxPackage(name="pkg2", spdx_id="SPDXRef-test-1")
        ]
    )

    errors, warnings = SpdxValidator.validate_document(doc)
    assert any("Duplicate SPDXID" in e for e in errors)
