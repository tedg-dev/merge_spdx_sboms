import pytest
from pathlib import Path
import tempfile
import json
from sbom_merger.infrastructure.file_handler import FileHandler


def test_discover_sbom_files_success(temp_sbom_dir):
    root_sbom, dep_sboms = FileHandler.discover_sbom_files(temp_sbom_dir)

    assert root_sbom.exists()
    assert root_sbom.name.endswith("_root.json")
    assert len(dep_sboms) > 0
    assert all(sbom.suffix == ".json" for sbom in dep_sboms)


def test_discover_sbom_files_not_dependencies_dir():
    with tempfile.TemporaryDirectory() as tmpdir:
        wrong_dir = Path(tmpdir) / "wrong_name"
        wrong_dir.mkdir()

        with pytest.raises(ValueError, match="must end with 'dependencies'"):
            FileHandler.discover_sbom_files(wrong_dir)


def test_discover_sbom_files_directory_not_found():
    non_existent = Path("/tmp/nonexistent_dir_12345/dependencies")

    with pytest.raises(FileNotFoundError, match="Dependencies directory not found"):
        FileHandler.discover_sbom_files(non_existent)


def test_discover_sbom_files_no_root():
    with tempfile.TemporaryDirectory() as tmpdir:
        deps_dir = Path(tmpdir) / "dependencies"
        deps_dir.mkdir()

        with pytest.raises(FileNotFoundError, match="No root SBOM found"):
            FileHandler.discover_sbom_files(deps_dir)


def test_discover_sbom_files_multiple_roots():
    with tempfile.TemporaryDirectory() as tmpdir:
        project_dir = Path(tmpdir) / "test_project"
        deps_dir = project_dir / "dependencies"
        deps_dir.mkdir(parents=True)

        (project_dir / "test1_root.json").write_text("{}")
        (project_dir / "test2_root.json").write_text("{}")

        with pytest.raises(ValueError, match="Multiple root SBOMs found"):
            FileHandler.discover_sbom_files(deps_dir)


def test_discover_sbom_files_no_dependencies():
    with tempfile.TemporaryDirectory() as tmpdir:
        project_dir = Path(tmpdir) / "test_project"
        deps_dir = project_dir / "dependencies"
        deps_dir.mkdir(parents=True)

        (project_dir / "test_root.json").write_text("{}")

        with pytest.raises(FileNotFoundError, match="No dependency SBOMs found"):
            FileHandler.discover_sbom_files(deps_dir)


def test_save_merged_sbom():
    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "output" / "merged.json"
        sbom_data = {"sbom": {"name": "test"}}

        FileHandler.save_merged_sbom(sbom_data, output_path)

        assert output_path.exists()
        with open(output_path) as f:
            loaded = json.load(f)
        assert loaded == sbom_data


def test_get_output_path_with_output_dir():
    with tempfile.TemporaryDirectory() as tmpdir:
        root_sbom = Path(tmpdir) / "test_root.json"
        output_dir = Path(tmpdir) / "output"

        result = FileHandler.get_output_path(root_sbom, output_dir)

        assert result.parent == output_dir
        assert "merged" in result.name


def test_get_output_path_without_output_dir():
    with tempfile.TemporaryDirectory() as tmpdir:
        root_sbom = Path(tmpdir) / "test_root.json"

        result = FileHandler.get_output_path(root_sbom, None)

        assert result.parent == root_sbom.parent
        assert "merged" in result.name
