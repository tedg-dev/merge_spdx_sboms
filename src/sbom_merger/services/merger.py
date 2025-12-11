import time
from pathlib import Path
from typing import List, Dict, Set
from datetime import datetime
from ..domain.models import (
    SpdxDocument,
    SpdxPackage,
    SpdxRelationship,
    MergeStatistics,
    MergeResult,
)
from .parser import SpdxParser
from .validator import SpdxValidator
from .id_generator import SpdxIdGenerator


class SbomMerger:

    def __init__(self):
        self.parser = SpdxParser()
        self.validator = SpdxValidator()
        self.id_generator = SpdxIdGenerator()

    def merge_sboms(
        self, root_sbom_path: Path, dependency_sbom_paths: List[Path]
    ) -> MergeResult:
        start_time = time.time()
        statistics = MergeStatistics()

        root_doc = self.parser.parse_sbom_file(root_sbom_path)
        statistics.root_packages_count = len(root_doc.packages)

        dep_docs = []
        for dep_path in dependency_sbom_paths:
            try:
                dep_doc = self.parser.parse_sbom_file(dep_path)
                dep_docs.append(dep_doc)
                statistics.dependency_packages_count += len(dep_doc.packages)
            except Exception as e:
                statistics.validation_errors.append(
                    f"Failed to parse {dep_path.name}: {str(e)}"
                )

        all_docs = [root_doc] + dep_docs
        statistics.total_sboms_processed = len(all_docs)

        errors, warnings = self.validator.validate_version_compatibility(all_docs)
        statistics.validation_errors.extend(errors)
        statistics.validation_warnings.extend(warnings)

        if errors:
            raise ValueError(
                f"Cannot merge SBOMs due to validation errors: " f"{'; '.join(errors)}"
            )

        merged_doc, duplicate_count = self._create_merged_document(root_doc, dep_docs)

        doc_errors, doc_warnings = self.validator.validate_document(merged_doc)
        statistics.validation_errors.extend(doc_errors)
        statistics.validation_warnings.extend(doc_warnings)

        statistics.total_packages = len(merged_doc.packages)
        statistics.total_relationships = len(merged_doc.relationships)
        statistics.duplicate_packages_removed = duplicate_count
        statistics.processing_time_seconds = time.time() - start_time

        return MergeResult(merged_document=merged_doc, statistics=statistics)

    def _create_merged_document(
        self, root_doc: SpdxDocument, dep_docs: List[SpdxDocument]
    ) -> tuple[SpdxDocument, int]:
        merged_packages = []
        merged_relationships = []
        id_mapping: Dict[str, str] = {}
        seen_ids: Set[str] = set()
        duplicate_count = 0

        for pkg in root_doc.packages:
            new_id = self.id_generator.generate_spdx_id(
                pkg.name, pkg.version_info, pkg.external_refs
            )
            id_mapping[pkg.spdx_id] = new_id

            if new_id not in seen_ids:
                merged_pkg = SpdxPackage(
                    name=pkg.name,
                    spdx_id=new_id,
                    download_location=pkg.download_location,
                    files_analyzed=pkg.files_analyzed,
                    version_info=pkg.version_info,
                    license_concluded=pkg.license_concluded,
                    copyright_text=pkg.copyright_text,
                    external_refs=pkg.external_refs,
                    source_sbom=pkg.source_sbom,
                )
                merged_packages.append(merged_pkg)
                seen_ids.add(new_id)

        for dep_doc in dep_docs:
            for pkg in dep_doc.packages:
                new_id = self.id_generator.generate_spdx_id(
                    pkg.name, pkg.version_info, pkg.external_refs
                )

                full_original_id = f"{dep_doc.source_file}::{pkg.spdx_id}"
                id_mapping[full_original_id] = new_id

                if new_id not in seen_ids:
                    merged_pkg = SpdxPackage(
                        name=pkg.name,
                        spdx_id=new_id,
                        download_location=pkg.download_location,
                        files_analyzed=pkg.files_analyzed,
                        version_info=pkg.version_info,
                        license_concluded=pkg.license_concluded,
                        copyright_text=pkg.copyright_text,
                        external_refs=pkg.external_refs,
                        source_sbom=pkg.source_sbom,
                    )
                    merged_packages.append(merged_pkg)
                    seen_ids.add(new_id)
                else:
                    duplicate_count += 1

        for rel in root_doc.relationships:
            element_id = id_mapping.get(rel.spdx_element_id, rel.spdx_element_id)
            related_id = id_mapping.get(
                rel.related_spdx_element, rel.related_spdx_element
            )

            if element_id == "SPDXRef-DOCUMENT":
                element_id = "SPDXRef-DOCUMENT"
            if related_id == "SPDXRef-DOCUMENT":
                related_id = "SPDXRef-DOCUMENT"

            merged_rel = SpdxRelationship(
                spdx_element_id=element_id,
                related_spdx_element=related_id,
                relationship_type=rel.relationship_type,
                source_sbom=rel.source_sbom,
            )
            merged_relationships.append(merged_rel)

        for dep_doc in dep_docs:
            for rel in dep_doc.relationships:
                element_key = f"{dep_doc.source_file}::{rel.spdx_element_id}"
                related_key = f"{dep_doc.source_file}::{rel.related_spdx_element}"

                element_id = id_mapping.get(element_key, rel.spdx_element_id)
                related_id = id_mapping.get(related_key, rel.related_spdx_element)

                merged_rel = SpdxRelationship(
                    spdx_element_id=element_id,
                    related_spdx_element=related_id,
                    relationship_type=rel.relationship_type,
                    source_sbom=rel.source_sbom,
                )
                merged_relationships.append(merged_rel)

        creation_info = root_doc.creation_info.copy()
        creation_info["created"] = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        if "creators" not in creation_info:
            creation_info["creators"] = []
        creation_info["creators"].append("Tool: merge-spdx-sboms-v1.0.0")

        merged_doc = SpdxDocument(
            spdx_version=root_doc.spdx_version,
            data_license=root_doc.data_license,
            spdx_id="SPDXRef-DOCUMENT",
            name=f"Merged SBOM: {root_doc.name}",
            document_namespace=self.id_generator.generate_document_namespace(
                root_doc.name
            ),
            creation_info=creation_info,
            packages=merged_packages,
            relationships=merged_relationships,
            comment=(
                f"Merged SBOM containing root and {len(dep_docs)} "
                f"dependency SBOMs. "
                f"{duplicate_count} duplicate packages removed. "
                f"Original root: {root_doc.source_file}"
            ),
        )

        return merged_doc, duplicate_count

    def _find_main_package(self, doc: SpdxDocument) -> str:
        for rel in doc.relationships:
            if (
                rel.spdx_element_id == "SPDXRef-DOCUMENT"
                and rel.relationship_type == "DESCRIBES"
            ):
                return rel.related_spdx_element

        if doc.packages:
            return doc.packages[-1].spdx_id

        return "SPDXRef-UNKNOWN"
