from pathlib import Path
import tempfile
from sbom_merger.services.reporter import MergeReporter
from sbom_merger.domain.models import MergeResult, MergeStatistics, SpdxDocument


def test_generate_report():
    doc = SpdxDocument(
        spdx_version="SPDX-2.3",
        data_license="CC0-1.0",
        spdx_id="SPDXRef-DOCUMENT",
        name="test",
        document_namespace="https://test.com",
        creation_info={"created": "2025-12-11T00:00:00Z"},
        comment="Test merge",
    )

    stats = MergeStatistics(
        total_sboms_processed=3,
        root_packages_count=10,
        dependency_packages_count=20,
        total_packages=30,
        total_relationships=15,
        processing_time_seconds=1.5,
    )

    result = MergeResult(merged_document=doc, statistics=stats)
    report = MergeReporter.generate_report(result)

    assert "SPDX SBOM Merge Report" in report
    assert "30" in report
    assert "15" in report
    assert "1.50 seconds" in report


def test_generate_report_with_errors():
    doc = SpdxDocument(
        spdx_version="SPDX-2.3",
        data_license="CC0-1.0",
        spdx_id="SPDXRef-DOCUMENT",
        name="test",
        document_namespace="https://test.com",
        creation_info={"created": "2025-12-11T00:00:00Z"},
    )

    stats = MergeStatistics(
        total_sboms_processed=2,
        validation_errors=["Error 1", "Error 2"],
        validation_warnings=["Warning 1"],
    )

    result = MergeResult(merged_document=doc, statistics=stats)
    report = MergeReporter.generate_report(result)

    assert "Error 1" in report
    assert "Warning 1" in report


def test_generate_report_saves_to_file():
    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "merged.json"

        doc = SpdxDocument(
            spdx_version="SPDX-2.3",
            data_license="CC0-1.0",
            spdx_id="SPDXRef-DOCUMENT",
            name="test",
            document_namespace="https://test.com",
            creation_info={"created": "2025-12-11T00:00:00Z"},
        )

        stats = MergeStatistics()
        result = MergeResult(merged_document=doc, statistics=stats)

        MergeReporter.generate_report(result, output_path)

        report_path = Path(tmpdir) / "merged_merge_report.md"
        assert report_path.exists()
