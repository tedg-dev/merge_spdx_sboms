from sbom_merger.services.merger import SbomMerger
from sbom_merger.infrastructure.file_handler import FileHandler


def test_merge_sboms(temp_sbom_dir):
    root_sbom, dep_sboms = FileHandler.discover_sbom_files(temp_sbom_dir)

    merger = SbomMerger()
    result = merger.merge_sboms(root_sbom, dep_sboms)

    assert result.merged_document is not None
    assert result.statistics.total_sboms_processed == 2
    assert result.statistics.total_packages > 0
    assert result.statistics.total_relationships > 0


def test_merge_creates_unique_ids(temp_sbom_dir):
    root_sbom, dep_sboms = FileHandler.discover_sbom_files(temp_sbom_dir)

    merger = SbomMerger()
    result = merger.merge_sboms(root_sbom, dep_sboms)

    spdx_ids = [pkg.spdx_id for pkg in result.merged_document.packages]
    assert len(spdx_ids) == len(set(spdx_ids))


def test_merge_preserves_relationships(temp_sbom_dir):
    root_sbom, dep_sboms = FileHandler.discover_sbom_files(temp_sbom_dir)

    merger = SbomMerger()
    result = merger.merge_sboms(root_sbom, dep_sboms)

    describes_rels = [
        r
        for r in result.merged_document.relationships
        if r.relationship_type == "DESCRIBES"
    ]
    assert len(describes_rels) >= 1

    depends_rels = [
        r
        for r in result.merged_document.relationships
        if r.relationship_type == "DEPENDS_ON"
    ]
    assert len(depends_rels) >= 2


def test_merge_validation(temp_sbom_dir):
    root_sbom, dep_sboms = FileHandler.discover_sbom_files(temp_sbom_dir)

    merger = SbomMerger()
    result = merger.merge_sboms(root_sbom, dep_sboms)

    assert result.merged_document.spdx_version == "SPDX-2.3"
    assert result.merged_document.spdx_id == "SPDXRef-DOCUMENT"
    assert result.merged_document.document_namespace is not None
