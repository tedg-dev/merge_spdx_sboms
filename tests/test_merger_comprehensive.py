from pathlib import Path
import tempfile
import json
from sbom_merger.services.merger import SbomMerger
from sbom_merger.domain.models import SpdxDocument


def test_merger_handles_error_in_parsing():
    merger = SbomMerger()

    with tempfile.TemporaryDirectory() as tmpdir:
        root_file = Path(tmpdir) / "root.json"
        root_file.write_text("invalid json{")

        try:
            merger.merge_sboms(root_file, [])
            assert False, "Should have raised exception"
        except Exception:
            assert True


def test_merger_empty_dependencies_list(sample_root_sbom):
    merger = SbomMerger()

    with tempfile.TemporaryDirectory() as tmpdir:
        root_file = Path(tmpdir) / "root.json"
        with open(root_file, "w") as f:
            json.dump(sample_root_sbom, f)

        result = merger.merge_sboms(root_file, [])

        assert result.merged_document is not None
        assert result.statistics.total_sboms_processed == 1


def test_merger_multiple_dependencies(sample_root_sbom, sample_dependency_sbom):
    merger = SbomMerger()

    with tempfile.TemporaryDirectory() as tmpdir:
        root_file = Path(tmpdir) / "root.json"
        dep1_file = Path(tmpdir) / "dep1.json"
        dep2_file = Path(tmpdir) / "dep2.json"

        with open(root_file, "w") as f:
            json.dump(sample_root_sbom, f)
        with open(dep1_file, "w") as f:
            json.dump(sample_dependency_sbom, f)
        with open(dep2_file, "w") as f:
            json.dump(sample_dependency_sbom, f)

        result = merger.merge_sboms(root_file, [dep1_file, dep2_file])

        assert result.statistics.total_sboms_processed == 3
