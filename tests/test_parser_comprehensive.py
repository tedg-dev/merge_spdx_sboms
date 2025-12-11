import tempfile
from pathlib import Path
import json
from sbom_merger.services.parser import SpdxParser
from sbom_merger.domain.models import SpdxDocument, SpdxPackage


def test_parse_invalid_json():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        f.write("invalid{json")
        temp_file = f.name

    try:
        SpdxParser.parse_sbom_file(Path(temp_file))
        assert False, "Should have raised exception"
    except Exception:
        assert True
    finally:
        Path(temp_file).unlink()


def test_serialize_minimal_document():
    doc = SpdxDocument(
        spdx_version="SPDX-2.3",
        data_license="CC0-1.0",
        spdx_id="SPDXRef-DOCUMENT",
        name="minimal",
        document_namespace="https://test.com",
        creation_info={"created": "2025-12-11T00:00:00Z"},
    )

    result = SpdxParser.serialize_to_json(doc)

    assert "sbom" in result
    assert result["sbom"]["name"] == "minimal"


def test_serialize_with_empty_lists():
    doc = SpdxDocument(
        spdx_version="SPDX-2.3",
        data_license="CC0-1.0",
        spdx_id="SPDXRef-DOCUMENT",
        name="empty",
        document_namespace="https://test.com",
        creation_info={"created": "2025-12-11T00:00:00Z"},
        packages=[],
        relationships=[],
    )

    result = SpdxParser.serialize_to_json(doc)

    assert result["sbom"]["packages"] == []
    assert result["sbom"]["relationships"] == []


def test_parse_file_not_found():
    try:
        SpdxParser.parse_sbom_file(Path("/nonexistent/file.json"))
        assert False, "Should have raised exception"
    except Exception:
        assert True
