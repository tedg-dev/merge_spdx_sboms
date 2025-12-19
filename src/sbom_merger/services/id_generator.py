import hashlib
import re
from typing import List, Optional, Any

# SPDX 2.3 Specification: SPDXID format is "SPDXRef-" + idstring
# idstring can only contain: letters (A-Za-z), numbers (0-9), dots (.), hyphens (-)
# Underscores are NOT allowed per SPDX 2.3 spec
SPDXID_ALLOWED_CHARS_PATTERN = re.compile(r"^[a-zA-Z0-9.-]+$")
SPDXID_FULL_PATTERN = re.compile(r"^SPDXRef-[a-zA-Z0-9.-]+$")


class SpdxIdGenerator:

    @staticmethod
    def sanitize_name(name: str) -> str:
        """Sanitize name for use in SPDXID.

        Per SPDX 2.3 spec, only A-Za-z0-9.- are allowed in the idstring.
        Underscores and other invalid characters are replaced with hyphens.
        """
        # Replace underscores and any invalid chars with hyphens
        sanitized = re.sub(r"[^a-zA-Z0-9.-]", "-", name)
        # Collapse multiple hyphens
        sanitized = re.sub(r"-+", "-", sanitized)
        # Remove leading/trailing hyphens
        return sanitized.strip("-")

    @staticmethod
    def is_valid_spdx_id(spdx_id: str) -> bool:
        """Validate that an SPDXID conforms to SPDX 2.3 spec.

        Format: "SPDXRef-" followed by idstring containing only A-Za-z0-9.-
        """
        return bool(SPDXID_FULL_PATTERN.match(spdx_id))

    @staticmethod
    def validate_spdx_id(spdx_id: str) -> List[str]:
        """Validate SPDXID and return list of errors (empty if valid)."""
        errors = []

        if not spdx_id:
            errors.append("SPDXID is empty")
            return errors

        if not spdx_id.startswith("SPDXRef-"):
            errors.append(f"SPDXID '{spdx_id}' must start with 'SPDXRef-'")
            return errors

        idstring = spdx_id[8:]  # Remove "SPDXRef-" prefix

        if not idstring:
            errors.append(f"SPDXID '{spdx_id}' has empty idstring after 'SPDXRef-'")
            return errors

        if "_" in idstring:
            errors.append(
                f"SPDXID '{spdx_id}' contains underscore(s) which are not allowed "
                "per SPDX 2.3 spec. Only A-Za-z0-9.- are permitted."
            )

        invalid_chars = re.findall(r"[^a-zA-Z0-9.-]", idstring)
        if invalid_chars:
            unique_invalid = set(invalid_chars)
            errors.append(
                f"SPDXID '{spdx_id}' contains invalid characters: {unique_invalid}. "
                "Only A-Za-z0-9.- are permitted per SPDX 2.3 spec."
            )

        return errors

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
