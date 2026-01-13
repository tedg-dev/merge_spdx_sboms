"""SPDX Specification Validator using spdx-tools library.

This module provides validation against the official SPDX specification
using the spdx-tools library. It supports SPDX 2.3 and is designed to be
extensible for future SPDX versions.
"""

import importlib.util
import json
import tempfile
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Any, Callable, Optional

from ..infrastructure.config import Config


@dataclass
class ValidationResult:
    """Result of SPDX specification validation."""

    is_valid: bool
    errors: List[str]
    warnings: List[str]
    spdx_version: str
    validator_used: str


class SpdxSpecValidator:
    """Validates SPDX documents against the official specification.

    Uses spdx-tools library for comprehensive validation including:
    - SPDXID format validation (no underscores per SPDX 2.3)
    - Required field validation
    - Relationship consistency
    - License expression validation
    - And other spec requirements
    """

    SUPPORTED_VERSIONS = ["SPDX-2.3"]

    def __init__(self, progress_callback: Optional[Callable[[str], None]] = None):
        self._spdx_tools_available = self._check_spdx_tools()
        self._progress_callback = progress_callback

    def _emit_progress(self, message: str):
        """Emit a progress message if callback is set."""
        if self._progress_callback:
            self._progress_callback(message)

    @staticmethod
    def _check_spdx_tools() -> bool:
        """Check if spdx-tools library is available."""
        return importlib.util.find_spec("spdx_tools") is not None

    def validate_json_file(self, file_path: Path) -> ValidationResult:
        """Validate an SPDX JSON file against the specification."""

        if not file_path.exists():
            return ValidationResult(
                is_valid=False,
                errors=[f"File not found: {file_path}"],
                warnings=[],
                spdx_version="unknown",
                validator_used="file_check",
            )

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                spdx_data = json.load(f)
        except json.JSONDecodeError as e:
            return ValidationResult(
                is_valid=False,
                errors=[f"Invalid JSON: {e}"],
                warnings=[],
                spdx_version="unknown",
                validator_used="json_parser",
            )

        return self.validate_json_data(spdx_data)

    def validate_json_data(self, spdx_data: Dict[str, Any]) -> ValidationResult:
        """Validate SPDX JSON data against the specification."""
        errors = []
        warnings = []

        # Get SPDX version
        spdx_version = spdx_data.get("spdxVersion", "unknown")

        # Calculate size for progress reporting
        num_packages = len(spdx_data.get("packages", []))
        num_relationships = len(spdx_data.get("relationships", []))

        # First, do our own SPDXID validation (catches underscores)
        self._emit_progress(f"Checking {num_packages} package IDs...")
        id_errors = self._validate_all_spdx_ids(spdx_data)
        errors.extend(id_errors)
        self._emit_progress("ID validation complete")

        # Then use spdx-tools for full spec validation
        if self._spdx_tools_available:
            if num_packages > 1000:
                # Estimate ~25% higher so users are happy when it finishes early
                est_minutes = max(1, (num_packages * 16) // 10000)
                self._emit_progress(
                    f"Running spdx-tools validation ({num_packages} packages, "
                    f"{num_relationships} relationships) - "
                    f"may take ~{est_minutes} minutes..."
                )
            else:
                self._emit_progress("Running spdx-tools validation...")
            spec_result = self._validate_with_spdx_tools(spdx_data)
            errors.extend(spec_result.errors)
            warnings.extend(spec_result.warnings)
            validator_used = "spdx-tools + custom"
        else:
            # Fallback to basic validation
            basic_result = self._basic_validation(spdx_data)
            errors.extend(basic_result.errors)
            warnings.extend(basic_result.warnings)
            warnings.append(
                "spdx-tools library not available. "
                "Using basic validation only. "
                "Install spdx-tools for full spec validation."
            )
            validator_used = "basic + custom"

        # Deduplicate errors
        errors = list(dict.fromkeys(errors))
        warnings = list(dict.fromkeys(warnings))

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            spdx_version=spdx_version,
            validator_used=validator_used,
        )

    def _validate_all_spdx_ids(self, spdx_data: Dict[str, Any]) -> List[str]:
        """Validate all SPDXIDs in the document for spec compliance.

        Per SPDX 2.3: SPDXID = "SPDXRef-" + idstring
        idstring can only contain: A-Za-z0-9.- (NO underscores)
        """
        from .id_generator import SpdxIdGenerator

        errors = []

        # Validate document SPDXID
        doc_spdx_id = spdx_data.get("SPDXID", "")
        if doc_spdx_id:
            id_errors = SpdxIdGenerator.validate_spdx_id(doc_spdx_id)
            for err in id_errors:
                errors.append(f"Document: {err}")

        # Validate package SPDXIDs
        packages = spdx_data.get("packages", [])
        total_packages = len(packages)
        for idx, pkg in enumerate(packages):
            pkg_spdx_id = pkg.get("SPDXID", "")
            pkg_name = pkg.get("name", "unknown")
            # Show progress every 500 packages or on last package
            if idx % 500 == 0 or idx == total_packages - 1:
                self._emit_progress(
                    f"Checking IDs: {idx + 1}/{total_packages} - {pkg_name[:40]}"
                )
            if pkg_spdx_id:
                id_errors = SpdxIdGenerator.validate_spdx_id(pkg_spdx_id)
                for err in id_errors:
                    errors.append(f"Package '{pkg_name}': {err}")

        # Validate relationship SPDXIDs
        relationships = spdx_data.get("relationships", [])
        for idx, rel in enumerate(relationships):
            element_id = rel.get("spdxElementId", "")
            related_id = rel.get("relatedSpdxElement", "")

            if element_id:
                id_errors = SpdxIdGenerator.validate_spdx_id(element_id)
                for err in id_errors:
                    errors.append(f"Relationship[{idx}] spdxElementId: {err}")

            if related_id:
                id_errors = SpdxIdGenerator.validate_spdx_id(related_id)
                for err in id_errors:
                    errors.append(f"Relationship[{idx}] relatedSpdxElement: {err}")

        return errors

    def _validate_with_spdx_tools(self, spdx_data: Dict[str, Any]) -> ValidationResult:
        """Validate using the spdx-tools library."""
        errors = []
        warnings = []
        stop_spinner = threading.Event()

        def spinner_thread():
            """Show progress spinner during long validation."""
            symbols = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
            idx = 0
            start_time = time.time()
            while not stop_spinner.is_set():
                elapsed = int(time.time() - start_time)
                minutes, seconds = divmod(elapsed, 60)
                if self._progress_callback:
                    self._progress_callback(
                        f"{symbols[idx]} Validating... ({minutes}m {seconds}s elapsed)"
                    )
                idx = (idx + 1) % len(symbols)
                stop_spinner.wait(0.5)

        try:
            from spdx_tools.spdx.parser.parse_anything import parse_file
            from spdx_tools.spdx.validation.document_validator import (
                validate_full_spdx_document,
            )

            # Write to temp file for spdx-tools parsing
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".spdx.json", delete=False
            ) as f:
                json.dump(spdx_data, f)
                temp_path = f.name

            try:
                # Start spinner for progress indication
                spinner = threading.Thread(target=spinner_thread, daemon=True)
                spinner.start()

                # Parse the document
                self._emit_progress("Parsing SPDX document...")
                document = parse_file(temp_path)

                # Validate against spec
                self._emit_progress("Running full spec validation...")
                validation_messages = validate_full_spdx_document(document)

                # Stop spinner
                stop_spinner.set()
                spinner.join(timeout=1)

                for msg in validation_messages:
                    msg_str = str(msg)
                    errors.append(f"[spdx-tools] {msg_str}")

            finally:
                stop_spinner.set()
                # Clean up temp file
                Path(temp_path).unlink(missing_ok=True)

        except ImportError as e:
            warnings.append(f"spdx-tools import error: {e}")
        except (ValueError, TypeError, KeyError) as e:
            errors.append(f"spdx-tools validation error: {e}")
        except Exception as e:
            # spdx-tools raises SPDXParsingError for invalid documents
            error_msg = str(e)
            if "SPDXParsingError" in type(e).__name__ or "parsing" in error_msg.lower():
                errors.append(f"[spdx-tools] SPDX parsing error: {error_msg}")
            else:
                errors.append(f"[spdx-tools] validation error: {error_msg}")

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            spdx_version=spdx_data.get("spdxVersion", "unknown"),
            validator_used="spdx-tools",
        )

    def _basic_validation(self, spdx_data: Dict[str, Any]) -> ValidationResult:
        """Basic validation without spdx-tools."""
        errors = []
        warnings = []

        # Required fields
        required_fields = [
            "spdxVersion",
            "SPDXID",
            "name",
            "dataLicense",
            "documentNamespace",
            "creationInfo",
        ]

        for field in required_fields:
            if field not in spdx_data:
                errors.append(f"Missing required field: {field}")

        # Validate SPDX version
        version = spdx_data.get("spdxVersion", "")
        if version and not Config.is_supported_spdx_version(version):
            if version in Config.FUTURE_SPDX_VERSIONS:
                warnings.append(f"SPDX version {version} not fully supported yet")
            else:
                errors.append(f"Unsupported SPDX version: {version}")

        # Validate packages have required fields
        packages = spdx_data.get("packages", [])
        for idx, pkg in enumerate(packages):
            if "SPDXID" not in pkg:
                errors.append(f"Package[{idx}] missing SPDXID")
            if "name" not in pkg:
                errors.append(f"Package[{idx}] missing name")
            if "downloadLocation" not in pkg:
                warnings.append(f"Package[{idx}] missing downloadLocation")

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            spdx_version=spdx_data.get("spdxVersion", "unknown"),
            validator_used="basic",
        )


def validate_spdx_output(output_path: Path) -> ValidationResult:
    """Convenience function to validate an SPDX output file.

    This is the main entry point for validating generated SBOMs.
    """
    validator = SpdxSpecValidator()
    return validator.validate_json_file(output_path)
