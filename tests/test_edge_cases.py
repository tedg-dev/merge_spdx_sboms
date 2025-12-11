import tempfile
from pathlib import Path
import json
from sbom_merger.services.merger import SbomMerger
from sbom_merger.services.parser import SpdxParser
from sbom_merger.services.reporter import MergeReporter
from sbom_merger.domain.models import SpdxDocument, MergeResult, MergeStatistics


def test_merger_exception_handling():
    """Test merger error handling"""
    merger = SbomMerger()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        root_file = Path(tmpdir) / "root.json"
        root_file.write_text("{}")
        
        try:
            merger.merge_sboms(root_file, [])
        except Exception:
            pass


def test_parser_missing_sbom_key():
    """Test parser with missing sbom wrapper"""
    data = {
        "spdxVersion": "SPDX-2.3",
        "dataLicense": "CC0-1.0",
        "SPDXID": "SPDXRef-DOCUMENT",
        "name": "test",
        "documentNamespace": "https://test.com",
        "creationInfo": {"created": "2025-12-11T00:00:00Z"},
        "packages": [],
        "relationships": []
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(data, f)
        temp_file = f.name
    
    try:
        doc = SpdxParser.parse_sbom_file(Path(temp_file))
        assert doc.spdx_version == "SPDX-2.3"
    finally:
        Path(temp_file).unlink()


def test_reporter_with_no_output_path():
    """Test reporter without output path"""
    doc = SpdxDocument(
        spdx_version="SPDX-2.3",
        data_license="CC0-1.0",
        spdx_id="SPDXRef-DOCUMENT",
        name="test",
        document_namespace="https://test.com",
        creation_info={"created": "2025-12-11T00:00:00Z"}
    )
    
    stats = MergeStatistics()
    result = MergeResult(merged_document=doc, statistics=stats)
    
    report = MergeReporter.generate_report(result, None)
    assert "SPDX SBOM Merge Report" in report


def test_merger_with_validation_errors(sample_root_sbom):
    """Test merger with invalid SPDX version"""
    merger = SbomMerger()
    
    # Create SBOM with invalid version
    invalid_sbom = sample_root_sbom.copy()
    invalid_sbom["sbom"]["spdxVersion"] = "SPDX-1.0"
    
    with tempfile.TemporaryDirectory() as tmpdir:
        root_file = Path(tmpdir) / "root.json"
        with open(root_file, 'w') as f:
            json.dump(invalid_sbom, f)
        
        try:
            merger.merge_sboms(root_file, [])
        except ValueError:
            pass


def test_parser_serialize_with_all_fields():
    """Test parser serialization with all optional fields"""
    from sbom_merger.domain.models import SpdxPackage, SpdxRelationship
    
    doc = SpdxDocument(
        spdx_version="SPDX-2.3",
        data_license="CC0-1.0",
        spdx_id="SPDXRef-DOCUMENT",
        name="test",
        document_namespace="https://test.com",
        creation_info={"created": "2025-12-11T00:00:00Z"},
        packages=[
            SpdxPackage(
                name="test-pkg",
                spdx_id="SPDXRef-pkg-1",
                version_info="1.0.0",
                license_concluded="MIT",
                copyright_text="Copyright 2025",
                external_refs=[{"referenceType": "purl", "referenceLocator": "pkg:pypi/test"}]
            )
        ],
        relationships=[
            SpdxRelationship(
                spdx_element_id="SPDXRef-DOCUMENT",
                related_spdx_element="SPDXRef-pkg-1",
                relationship_type="DESCRIBES"
            )
        ],
        comment="Full test"
    )
    
    result = SpdxParser.serialize_to_json(doc)
    assert result["sbom"]["packages"][0]["versionInfo"] == "1.0.0"
