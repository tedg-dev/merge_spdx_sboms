from typing import List, Tuple
from ..domain.models import SpdxDocument
from ..infrastructure.config import Config


class SpdxValidator:

    @staticmethod
    def validate_document(document: SpdxDocument) -> Tuple[List[str], List[str]]:
        errors = []
        warnings = []

        if not Config.is_supported_spdx_version(document.spdx_version):
            if document.spdx_version in Config.FUTURE_SPDX_VERSIONS:
                warnings.append(
                    f"SPDX version {document.spdx_version} is not yet supported. "
                    f"Supported versions: {', '.join(Config.SUPPORTED_SPDX_VERSIONS)}"
                )
            else:
                errors.append(
                    f"Unsupported SPDX version: {document.spdx_version}. "
                    f"Supported: {', '.join(Config.SUPPORTED_SPDX_VERSIONS)}"
                )

        if not document.spdx_id:
            errors.append("Document SPDXID is missing")

        if not document.document_namespace:
            errors.append("Document namespace is missing")

        if not document.name:
            warnings.append("Document name is empty")

        if not document.packages:
            warnings.append("Document contains no packages")

        spdx_ids = set()
        for pkg in document.packages:
            if not pkg.spdx_id:
                errors.append(f"Package '{pkg.name}' is missing SPDXID")
            elif pkg.spdx_id in spdx_ids:
                errors.append(f"Duplicate SPDXID found: {pkg.spdx_id}")
            else:
                spdx_ids.add(pkg.spdx_id)

            if not pkg.name:
                errors.append(f"Package with SPDXID '{pkg.spdx_id}' has no name")

        all_ids = {pkg.spdx_id for pkg in document.packages}
        all_ids.add(document.spdx_id)

        for rel in document.relationships:
            if rel.spdx_element_id not in all_ids:
                warnings.append(
                    f"Relationship references unknown SPDXID: "
                    f"{rel.spdx_element_id}. "
                    f"Relationship element '{rel.spdx_element_id}' "
                    f"not found in document packages"
                )
            if rel.related_spdx_element not in all_ids:
                warnings.append(
                    f"Relationship references unknown SPDXID: "
                    f"{rel.related_spdx_element}. "
                    f"Related element '{rel.related_spdx_element}' "
                    f"not found in document packages"
                )

        return errors, warnings

    @staticmethod
    def validate_version_compatibility(
        documents: List[SpdxDocument],
    ) -> Tuple[List[str], List[str]]:
        errors = []
        warnings = []

        versions = {doc.spdx_version for doc in documents}

        if len(versions) > 1:
            warnings.append(
                f"Multiple SPDX versions detected: {', '.join(versions)}. "
                "This may cause compatibility issues."
            )

        for doc in documents:
            if not Config.is_supported_spdx_version(doc.spdx_version):
                supported = ', '.join(Config.SUPPORTED_SPDX_VERSIONS)
                errors.append(
                    f"Unsupported SPDX version: {doc.spdx_version}. "
                    f"Supported versions: {supported}"
                )

        return errors, warnings
