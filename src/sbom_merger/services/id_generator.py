import hashlib
import re
from typing import List, Optional, Any


class SpdxIdGenerator:

    @staticmethod
    def sanitize_name(name: str) -> str:
        sanitized = re.sub(r"[^a-zA-Z0-9-_.]", "-", name)
        sanitized = re.sub(r"-+", "-", sanitized)
        return sanitized.strip("-")

    @staticmethod
    def extract_ecosystem(external_refs: list) -> str:
        for ref in external_refs:
            if ref.get("referenceType") == "purl":
                purl = ref.get("referenceLocator", "")
                if purl.startswith("pkg:"):
                    ecosystem: str = purl.split(":")[1].split("/")[0]
                    return ecosystem
        return "unknown"

    @staticmethod
    def generate_hash(name: str, version: Optional[str] = None) -> str:
        content = f"{name}:{version}" if version else name
        hash_value: str = hashlib.sha256(content.encode()).hexdigest()[:6]
        return hash_value

    @staticmethod
    def generate_spdx_id(
        name: str,
        version: Optional[str] = None,
        external_refs: Optional[List[Any]] = None,
    ) -> str:
        ecosystem = SpdxIdGenerator.extract_ecosystem(external_refs or [])
        sanitized_name = SpdxIdGenerator.sanitize_name(name)
        hash_suffix = SpdxIdGenerator.generate_hash(name, version)

        return f"SPDXRef-{ecosystem}-{sanitized_name}-{hash_suffix}"

    @staticmethod
    def generate_document_namespace(base_name: str) -> str:
        import uuid

        unique_id = str(uuid.uuid4())
        return f"https://spdx.org/spdxdocs/merged-sbom/{unique_id}"
