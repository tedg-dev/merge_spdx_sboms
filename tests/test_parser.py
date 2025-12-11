import pytest
import json
import tempfile
from pathlib import Path
from sbom_merger.services.parser import SpdxParser
from sbom_merger.domain.models import SpdxDocument, SpdxPackage


def test_parse_sbom_file_with_sbom_wrapper(sample_root_sbom):
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(sample_root_sbom, f)
        temp_file = f.name

    try:
        doc = SpdxParser.parse_sbom_file(Path(temp_file))
        assert doc.spdx_version == "SPDX-2.3"
        assert len(doc.packages) > 0
        assert len(doc.relationships) > 0
    finally:
        Path(temp_file).unlink()


def test_parse_sbom_file_without_wrapper():
    data = {
        "spdxVersion": "SPDX-2.3",
        "dataLicense": "CC0-1.0",
        "SPDXID": "SPDXRef-DOCUMENT",
        "name": "test",
        "documentNamespace": "https://test.com",
        "creationInfo": {"created": "2025-12-11T00:00:00Z"},
        "packages": [],
        "relationships": [],
    }

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(data, f)
        temp_file = f.name

    try:
        doc = SpdxParser.parse_sbom_file(Path(temp_file))
        assert doc.spdx_version == "SPDX-2.3"
    finally:
        Path(temp_file).unlink()


def test_serialize_to_json():
    doc = SpdxDocument(
        spdx_version="SPDX-2.3",
        data_license="CC0-1.0",
        spdx_id="SPDXRef-DOCUMENT",
        name="test",
        document_namespace="https://test.com",
        creation_info={"created": "2025-12-11T00:00:00Z"},
        packages=[
            SpdxPackage(name="test-pkg", spdx_id="SPDXRef-test-1", version_info="1.0.0")
        ],
        comment="Test comment",
    )

    result = SpdxParser.serialize_to_json(doc)

    assert "sbom" in result
    assert result["sbom"]["spdxVersion"] == "SPDX-2.3"
    assert len(result["sbom"]["packages"]) == 1
    assert result["sbom"]["comment"] == "Test comment"
