import json
from pathlib import Path
from typing import List, Tuple, Optional


class FileHandler:

    @staticmethod
    def discover_sbom_files(dependencies_dir: Path) -> Tuple[Path, List[Path]]:
        if not dependencies_dir.exists():
            raise FileNotFoundError(
                f"Dependencies directory not found: {dependencies_dir}"
            )

        if dependencies_dir.name != "dependencies":
            raise ValueError(
                "Path must end with 'dependencies' directory. "
                f"Got: {dependencies_dir.name}"
            )

        parent_dir = dependencies_dir.parent

        root_sbom_pattern = "*_root.json"
        root_sboms = list(parent_dir.glob(root_sbom_pattern))

        if not root_sboms:
            raise FileNotFoundError(
                f"No root SBOM found matching pattern '{root_sbom_pattern}' "
                f"in {parent_dir}"
            )

        if len(root_sboms) > 1:
            raise ValueError(
                f"Multiple root SBOMs found in {parent_dir}: "
                f"{[s.name for s in root_sboms]}"
            )

        root_sbom = root_sboms[0]

        dependency_sboms = [f for f in dependencies_dir.glob("*.json") if f.is_file()]

        if not dependency_sboms:
            raise FileNotFoundError(f"No dependency SBOMs found in {dependencies_dir}")

        return root_sbom, dependency_sboms

    @staticmethod
    def save_merged_sbom(sbom_data: dict, output_path: Path) -> None:
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(sbom_data, f, indent=2)

    @staticmethod
    def get_output_path(
        root_sbom_path: Path, output_dir: Optional[Path] = None
    ) -> Path:
        if output_dir:
            output_dir.mkdir(parents=True, exist_ok=True)
            base_name = root_sbom_path.stem.replace("_root", "_merged")
            return output_dir / f"{base_name}.json"
        else:
            parent = root_sbom_path.parent
            base_name = root_sbom_path.stem.replace("_root", "_merged")
            return parent / f"{base_name}.json"
