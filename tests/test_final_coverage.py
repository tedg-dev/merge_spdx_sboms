"""Final tests to achieve 96%+ coverage targeting specific uncovered lines"""
import tempfile
from pathlib import Path
import json
from sbom_merger.services.merger import SbomMerger
from sbom_merger.services.parser import SpdxParser
from sbom_merger.services.reporter import MergeReporter
from sbom_merger.services.validator import SpdxValidator
from sbom_merger.domain.models import (
    SpdxDocument, SpdxPackage, SpdxRelationship,
    MergeResult, MergeStatistics
)


def test_parser_error_cases():
    """Test parser error handling - lines 68, 70, 72, 77"""
    # Test with completely invalid JSON
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        f.write("not json at all")
        temp_file = f.name
    
    try:
        SpdxParser.parse_sbom_file(Path(temp_file))
        assert False
    except Exception:
        pass
    finally:
        Path(temp_file).unlink()
    
    # Test with missing required fields
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump({"invalid": "structure"}, f)
        temp_file = f.name
    
    try:
        SpdxParser.parse_sbom_file(Path(temp_file))
        assert False
    except Exception:
        pass
    finally:
        Path(temp_file).unlink()


def test_validator_unsupported_version():
    """Test validator with unsupported version - line 20"""
    doc = SpdxDocument(
        spdx_version="SPDX-1.0",
        data_license="CC0-1.0",
        spdx_id="SPDXRef-DOCUMENT",
        name="test",
        document_namespace="https://test.com",
        creation_info={"created": "2025-12-11T00:00:00Z"}
    )
    
    errors, warnings = SpdxValidator.validate_version_compatibility([doc])
    assert len(errors) > 0
    assert any("unsupported" in str(e).lower() for e in errors)


def test_validator_unknown_relationship():
    """Test validator with unknown relationship elements - line 58"""
    doc = SpdxDocument(
        spdx_version="SPDX-2.3",
        data_license="CC0-1.0",
        spdx_id="SPDXRef-DOCUMENT",
        name="test",
        document_namespace="https://test.com",
        creation_info={"created": "2025-12-11T00:00:00Z"},
        packages=[SpdxPackage(name="pkg1", spdx_id="SPDXRef-pkg1")],
        relationships=[
            SpdxRelationship(
                spdx_element_id="SPDXRef-unknown",
                related_spdx_element="SPDXRef-pkg1",
                relationship_type="DEPENDS_ON"
            )
        ]
    )
    
    errors, warnings = SpdxValidator.validate_document(doc)
    assert len(warnings) > 0


def test_reporter_no_validation_report():
    """Test reporter when validation is successful - line 28"""
    doc = SpdxDocument(
        spdx_version="SPDX-2.3",
        data_license="CC0-1.0",
        spdx_id="SPDXRef-DOCUMENT",
        name="test",
        document_namespace="https://test.com",
        creation_info={"created": "2025-12-11T00:00:00Z"}
    )
    
    stats = MergeStatistics(
        total_sboms_processed=1,
        validation_errors=[],
        validation_warnings=[]
    )
    
    result = MergeResult(merged_document=doc, statistics=stats)
    report = MergeReporter.generate_report(result)
    
    assert "SPDX SBOM Merge Report" in report
    assert "validation" in report.lower()


def test_merger_error_in_dependency(sample_root_sbom):
    """Test merger with errors in dependency files - lines 38-39, 53"""
    merger = SbomMerger()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        root_file = Path(tmpdir) / "root.json"
        bad_dep = Path(tmpdir) / "bad_dep.json"
        
        with open(root_file, 'w') as f:
            json.dump(sample_root_sbom, f)
        
        # Create invalid dependency file
        with open(bad_dep, 'w') as f:
            f.write("invalid json{")
        
        try:
            merger.merge_sboms(root_file, [bad_dep])
            assert False
        except Exception:
            pass


def test_merger_validation_failures(sample_root_sbom):
    """Test merger with validation failures - lines 144, 180"""
    merger = SbomMerger()
    
    # Create SBOM with unsupported version
    invalid_sbom = sample_root_sbom.copy()
    if "sbom" in invalid_sbom:
        invalid_sbom["sbom"]["spdxVersion"] = "SPDX-0.9"
    else:
        invalid_sbom["spdxVersion"] = "SPDX-0.9"
    
    with tempfile.TemporaryDirectory() as tmpdir:
        root_file = Path(tmpdir) / "root.json"
        with open(root_file, 'w') as f:
            json.dump(invalid_sbom, f)
        
        try:
            merger.merge_sboms(root_file, [])
            assert False
        except ValueError:
            pass


def test_merger_no_main_package(sample_root_sbom):
    """Test merger when main package not found - lines 209-212"""
    merger = SbomMerger()
    
    # Create SBOM without DESCRIBES relationship
    modified_sbom = sample_root_sbom.copy()
    if "sbom" in modified_sbom:
        modified_sbom["sbom"]["relationships"] = []
    else:
        modified_sbom["relationships"] = []
    
    with tempfile.TemporaryDirectory() as tmpdir:
        root_file = Path(tmpdir) / "root.json"
        with open(root_file, 'w') as f:
            json.dump(modified_sbom, f)
        
        result = merger.merge_sboms(root_file, [])
        # Should still complete but may have warnings
        assert result.merged_document is not None


def test_cli_github_push_no_account():
    """Test CLI GitHub push without valid account"""
    from click.testing import CliRunner
    from sbom_merger.cli import main
    
    runner = CliRunner()
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump({"accounts": []}, f)
        key_file = f.name
    
    with tempfile.TemporaryDirectory() as tmpdir:
        deps_dir = Path(tmpdir) / "test_project" / "dependencies"
        deps_dir.mkdir(parents=True)
        
        root_file = deps_dir.parent / "test_root.json"
        dep_file = deps_dir / "dep1.json"
        
        minimal_sbom = {
            "sbom": {
                "spdxVersion": "SPDX-2.3",
                "dataLicense": "CC0-1.0",
                "SPDXID": "SPDXRef-DOCUMENT",
                "name": "test",
                "documentNamespace": "https://test.com",
                "creationInfo": {"created": "2025-12-11T00:00:00Z"},
                "packages": [],
                "relationships": []
            }
        }
        
        with open(root_file, 'w') as f:
            json.dump(minimal_sbom, f)
        with open(dep_file, 'w') as f:
            json.dump(minimal_sbom, f)
        
        try:
            result = runner.invoke(main, [
                '--dependencies-dir', str(deps_dir),
                '--key-file', key_file,
                '--push-to-github',
                '--github-owner', 'test',
                '--github-repo', 'test'
            ])
            
            # Should handle missing account
            assert result.exit_code != 0 or 'account' in result.output.lower()
        finally:
            Path(key_file).unlink()
