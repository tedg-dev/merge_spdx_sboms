import json
from pathlib import Path
from typing import Dict, Any
from ..domain.models import SpdxDocument, SpdxPackage, SpdxRelationship


class SpdxParser:

    @staticmethod
    def parse_sbom_file(file_path: Path) -> SpdxDocument:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if "sbom" in data:
            sbom_data = data["sbom"]
        else:
            sbom_data = data

        packages = []
        for pkg_data in sbom_data.get("packages", []):
            packages.append(
                SpdxPackage(
                    name=pkg_data.get("name", ""),
                    spdx_id=pkg_data.get("SPDXID", ""),
                    download_location=pkg_data.get("downloadLocation", "NOASSERTION"),
                    files_analyzed=pkg_data.get("filesAnalyzed", False),
                    version_info=pkg_data.get("versionInfo"),
                    license_concluded=pkg_data.get("licenseConcluded"),
                    copyright_text=pkg_data.get("copyrightText"),
                    external_refs=pkg_data.get("externalRefs", []),
                    source_sbom=file_path.name,
                )
            )

        relationships = []
        for rel_data in sbom_data.get("relationships", []):
            relationships.append(
                SpdxRelationship(
                    spdx_element_id=rel_data.get("spdxElementId", ""),
                    related_spdx_element=rel_data.get("relatedSpdxElement", ""),
                    relationship_type=rel_data.get("relationshipType", ""),
                    source_sbom=file_path.name,
                )
            )

        return SpdxDocument(
            spdx_version=sbom_data.get("spdxVersion", ""),
            data_license=sbom_data.get("dataLicense", "CC0-1.0"),
            spdx_id=sbom_data.get("SPDXID", "SPDXRef-DOCUMENT"),
            name=sbom_data.get("name", ""),
            document_namespace=sbom_data.get("documentNamespace", ""),
            creation_info=sbom_data.get("creationInfo", {}),
            packages=packages,
            relationships=relationships,
            comment=sbom_data.get("comment"),
            source_file=file_path.name,
        )

    @staticmethod
    def serialize_to_json(document: SpdxDocument) -> Dict[str, Any]:
        packages_data = []
        for pkg in document.packages:
            pkg_dict = {
                "name": pkg.name,
                "SPDXID": pkg.spdx_id,
                "downloadLocation": pkg.download_location,
                "filesAnalyzed": pkg.files_analyzed,
            }
            if pkg.version_info:
                pkg_dict["versionInfo"] = pkg.version_info
            if pkg.license_concluded:
                pkg_dict["licenseConcluded"] = pkg.license_concluded
            if pkg.copyright_text:
                pkg_dict["copyrightText"] = pkg.copyright_text
            if pkg.external_refs:
                pkg_dict["externalRefs"] = pkg.external_refs
            packages_data.append(pkg_dict)

        relationships_data = []
        for rel in document.relationships:
            relationships_data.append(
                {
                    "spdxElementId": rel.spdx_element_id,
                    "relatedSpdxElement": rel.related_spdx_element,
                    "relationshipType": rel.relationship_type,
                }
            )

        sbom_dict = {
            "spdxVersion": document.spdx_version,
            "dataLicense": document.data_license,
            "SPDXID": document.spdx_id,
            "name": document.name,
            "documentNamespace": document.document_namespace,
            "creationInfo": document.creation_info,
            "packages": packages_data,
            "relationships": relationships_data,
        }

        if document.comment:
            sbom_dict["comment"] = document.comment

        return {"sbom": sbom_dict}
