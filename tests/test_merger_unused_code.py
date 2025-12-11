"""Tests for unused/uncovered merger code paths"""
import tempfile
from pathlib import Path
import json
from sbom_merger.services.merger import SbomMerger
from sbom_merger.domain.models import SpdxDocument, SpdxPackage, SpdxRelationship


def test_find_main_package_with_describes_relationship():
    """Test _find_main_package when DESCRIBES relationship exists"""
    merger = SbomMerger()
    
    doc = SpdxDocument(
        spdx_version="SPDX-2.3",
        data_license="CC0-1.0",
        spdx_id="SPDXRef-DOCUMENT",
        name="test",
        document_namespace="https://test.com",
        creation_info={"created": "2025-12-11T00:00:00Z"},
        packages=[
            SpdxPackage(name="pkg1", spdx_id="SPDXRef-pkg1")
        ],
        relationships=[
            SpdxRelationship(
                spdx_element_id="SPDXRef-DOCUMENT",
                related_spdx_element="SPDXRef-pkg1",
                relationship_type="DESCRIBES"
            )
        ]
    )
    
    main_pkg = merger._find_main_package(doc)
    assert main_pkg == "SPDXRef-pkg1"


def test_find_main_package_fallback_to_last_package():
    """Test _find_main_package falls back to last package when no DESCRIBES"""
    merger = SbomMerger()
    
    doc = SpdxDocument(
        spdx_version="SPDX-2.3",
        data_license="CC0-1.0",
        spdx_id="SPDXRef-DOCUMENT",
        name="test",
        document_namespace="https://test.com",
        creation_info={"created": "2025-12-11T00:00:00Z"},
        packages=[
            SpdxPackage(name="pkg1", spdx_id="SPDXRef-pkg1"),
            SpdxPackage(name="pkg2", spdx_id="SPDXRef-pkg2")
        ],
        relationships=[]
    )
    
    main_pkg = merger._find_main_package(doc)
    assert main_pkg == "SPDXRef-pkg2"


def test_find_main_package_no_packages():
    """Test _find_main_package returns UNKNOWN when no packages"""
    merger = SbomMerger()
    
    doc = SpdxDocument(
        spdx_version="SPDX-2.3",
        data_license="CC0-1.0",
        spdx_id="SPDXRef-DOCUMENT",
        name="test",
        document_namespace="https://test.com",
        creation_info={"created": "2025-12-11T00:00:00Z"},
        packages=[],
        relationships=[]
    )
    
    main_pkg = merger._find_main_package(doc)
    assert main_pkg == "SPDXRef-UNKNOWN"


def test_merge_with_document_relationships():
    """Test merging preserves SPDXRef-DOCUMENT relationships"""
    merger = SbomMerger()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        root_file = Path(tmpdir) / "root.json"
        
        root_sbom = {
            "sbom": {
                "spdxVersion": "SPDX-2.3",
                "dataLicense": "CC0-1.0",
                "SPDXID": "SPDXRef-DOCUMENT",
                "name": "test-root",
                "documentNamespace": "https://test.com/root",
                "creationInfo": {"created": "2025-12-11T00:00:00Z"},
                "packages": [
                    {
                        "name": "test-package",
                        "SPDXID": "SPDXRef-Package",
                        "downloadLocation": "NOASSERTION",
                        "filesAnalyzed": False
                    }
                ],
                "relationships": [
                    {
                        "spdxElementId": "SPDXRef-DOCUMENT",
                        "relatedSpdxElement": "SPDXRef-Package",
                        "relationshipType": "DESCRIBES"
                    },
                    {
                        "spdxElementId": "SPDXRef-Package",
                        "relatedSpdxElement": "SPDXRef-DOCUMENT",
                        "relationshipType": "DESCRIBED_BY"
                    }
                ]
            }
        }
        
        with open(root_file, 'w') as f:
            json.dump(root_sbom, f)
        
        result = merger.merge_sboms(root_file, [])
        
        # Check that DOCUMENT relationships are preserved
        doc_relationships = [
            rel for rel in result.merged_document.relationships
            if rel.spdx_element_id == "SPDXRef-DOCUMENT" or 
               rel.related_spdx_element == "SPDXRef-DOCUMENT"
        ]
        
        assert len(doc_relationships) >= 1
        assert result.statistics.total_relationships > 0
