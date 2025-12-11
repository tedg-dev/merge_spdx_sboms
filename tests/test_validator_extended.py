import pytest
from sbom_merger.services.validator import SpdxValidator
from sbom_merger.domain.models import SpdxDocument, SpdxPackage, SpdxRelationship


def test_validate_document_missing_spdx_id():
    doc = SpdxDocument(
        spdx_version="SPDX-2.3",
        data_license="CC0-1.0",
        spdx_id="",
        name="test",
        document_namespace="https://test.com/test",
        creation_info={"created": "2025-12-11T00:00:00Z"},
    )

    errors, warnings = SpdxValidator.validate_document(doc)
    assert any("SPDXID is missing" in e for e in errors)


def test_validate_document_missing_namespace():
    doc = SpdxDocument(
        spdx_version="SPDX-2.3",
        data_license="CC0-1.0",
        spdx_id="SPDXRef-DOCUMENT",
        name="test",
        document_namespace="",
        creation_info={"created": "2025-12-11T00:00:00Z"},
    )

    errors, warnings = SpdxValidator.validate_document(doc)
    assert any("namespace is missing" in e for e in errors)


def test_validate_document_empty_name():
    doc = SpdxDocument(
        spdx_version="SPDX-2.3",
        data_license="CC0-1.0",
        spdx_id="SPDXRef-DOCUMENT",
        name="",
        document_namespace="https://test.com/test",
        creation_info={"created": "2025-12-11T00:00:00Z"},
    )

    errors, warnings = SpdxValidator.validate_document(doc)
    assert any("name is empty" in w for w in warnings)


def test_validate_document_no_packages():
    doc = SpdxDocument(
        spdx_version="SPDX-2.3",
        data_license="CC0-1.0",
        spdx_id="SPDXRef-DOCUMENT",
        name="test",
        document_namespace="https://test.com/test",
        creation_info={"created": "2025-12-11T00:00:00Z"},
        packages=[],
    )

    errors, warnings = SpdxValidator.validate_document(doc)
    assert any("no packages" in w for w in warnings)


def test_validate_document_package_missing_spdxid():
    doc = SpdxDocument(
        spdx_version="SPDX-2.3",
        data_license="CC0-1.0",
        spdx_id="SPDXRef-DOCUMENT",
        name="test",
        document_namespace="https://test.com/test",
        creation_info={"created": "2025-12-11T00:00:00Z"},
        packages=[SpdxPackage(name="test-pkg", spdx_id="")],
    )

    errors, warnings = SpdxValidator.validate_document(doc)
    assert any("missing SPDXID" in e for e in errors)


def test_validate_document_package_no_name():
    doc = SpdxDocument(
        spdx_version="SPDX-2.3",
        data_license="CC0-1.0",
        spdx_id="SPDXRef-DOCUMENT",
        name="test",
        document_namespace="https://test.com/test",
        creation_info={"created": "2025-12-11T00:00:00Z"},
        packages=[SpdxPackage(name="", spdx_id="SPDXRef-test-1")],
    )

    errors, warnings = SpdxValidator.validate_document(doc)
    assert any("has no name" in e for e in errors)


def test_validate_document_unknown_relationship_element():
    doc = SpdxDocument(
        spdx_version="SPDX-2.3",
        data_license="CC0-1.0",
        spdx_id="SPDXRef-DOCUMENT",
        name="test",
        document_namespace="https://test.com/test",
        creation_info={"created": "2025-12-11T00:00:00Z"},
        packages=[SpdxPackage(name="test-pkg", spdx_id="SPDXRef-test-1")],
        relationships=[
            SpdxRelationship(
                spdx_element_id="SPDXRef-unknown",
                related_spdx_element="SPDXRef-test-1",
                relationship_type="DEPENDS_ON",
            )
        ],
    )

    errors, warnings = SpdxValidator.validate_document(doc)
    assert any("unknown SPDXID" in w for w in warnings)


def test_validate_version_compatibility_multiple_versions():
    doc1 = SpdxDocument(
        spdx_version="SPDX-2.3",
        data_license="CC0-1.0",
        spdx_id="SPDXRef-DOCUMENT",
        name="test1",
        document_namespace="https://test.com/test1",
        creation_info={"created": "2025-12-11T00:00:00Z"},
    )

    doc2 = SpdxDocument(
        spdx_version="SPDX-2.2",
        data_license="CC0-1.0",
        spdx_id="SPDXRef-DOCUMENT",
        name="test2",
        document_namespace="https://test.com/test2",
        creation_info={"created": "2025-12-11T00:00:00Z"},
    )

    errors, warnings = SpdxValidator.validate_version_compatibility([doc1, doc2])
    assert any("Multiple SPDX versions" in w for w in warnings)


def test_validate_version_compatibility_unsupported():
    doc = SpdxDocument(
        spdx_version="SPDX-1.2",
        data_license="CC0-1.0",
        spdx_id="SPDXRef-DOCUMENT",
        name="test",
        document_namespace="https://test.com/test",
        creation_info={"created": "2025-12-11T00:00:00Z"},
    )

    errors, warnings = SpdxValidator.validate_version_compatibility([doc])
    assert any("unsupported version" in e for e in errors)
