from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any


@dataclass
class SpdxPackage:
    name: str
    spdx_id: str
    download_location: str = "NOASSERTION"
    files_analyzed: bool = False
    version_info: Optional[str] = None
    license_concluded: Optional[str] = None
    copyright_text: Optional[str] = None
    external_refs: List[Dict[str, str]] = field(default_factory=list)
    source_sbom: Optional[str] = None


@dataclass
class SpdxRelationship:
    spdx_element_id: str
    related_spdx_element: str
    relationship_type: str
    source_sbom: Optional[str] = None


@dataclass
class SpdxDocument:
    spdx_version: str
    data_license: str
    spdx_id: str
    name: str
    document_namespace: str
    creation_info: Dict[str, Any]
    packages: List[SpdxPackage] = field(default_factory=list)
    relationships: List[SpdxRelationship] = field(default_factory=list)
    comment: Optional[str] = None
    source_file: Optional[str] = None


@dataclass
class MergeStatistics:
    total_sboms_processed: int = 0
    root_packages_count: int = 0
    dependency_packages_count: int = 0
    total_packages: int = 0
    total_relationships: int = 0
    duplicate_packages_removed: int = 0
    processing_time_seconds: float = 0.0
    validation_errors: List[str] = field(default_factory=list)
    validation_warnings: List[str] = field(default_factory=list)


@dataclass
class MergeResult:
    merged_document: SpdxDocument
    statistics: MergeStatistics
    output_path: Optional[str] = None
