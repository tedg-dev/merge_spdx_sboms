import pytest
from sbom_merger.services.id_generator import SpdxIdGenerator


def test_sanitize_name():
    assert SpdxIdGenerator.sanitize_name("test-package") == "test-package"
    assert SpdxIdGenerator.sanitize_name("@scope/package") == "scope-package"
    assert SpdxIdGenerator.sanitize_name("package_name") == "package_name"


def test_extract_ecosystem():
    refs = [
        {
            "referenceType": "purl",
            "referenceLocator": "pkg:pypi/requests"
        }
    ]
    assert SpdxIdGenerator.extract_ecosystem(refs) == "pypi"

    refs = [
        {
            "referenceType": "purl",
            "referenceLocator": "pkg:npm/lodash"
        }
    ]
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
    refs = [
        {
            "referenceType": "purl",
            "referenceLocator": "pkg:pypi/requests@2.31.0"
        }
    ]

    spdx_id = SpdxIdGenerator.generate_spdx_id(
        "requests",
        "2.31.0",
        refs
    )

    assert spdx_id.startswith("SPDXRef-pypi-")
    assert "requests" in spdx_id
    assert len(spdx_id.split("-")[-1]) == 6


def test_generate_document_namespace():
    namespace = SpdxIdGenerator.generate_document_namespace("test-sbom")

    assert namespace.startswith("https://spdx.org/spdxdocs/merged-sbom/")
    assert len(namespace) > 50
