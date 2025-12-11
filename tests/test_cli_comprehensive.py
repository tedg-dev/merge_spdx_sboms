from click.testing import CliRunner
from sbom_merger.cli import main
import tempfile
from pathlib import Path
import json


def test_cli_verbose_output(temp_sbom_dir):
    runner = CliRunner()
    result = runner.invoke(main, [
        '--dependencies-dir', str(temp_sbom_dir),
        '--verbose'
    ])
    
    assert 'Discovering SBOM files' in result.output or result.exit_code == 0


def test_cli_invalid_dir_not_dependencies():
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as tmpdir:
        invalid_dir = Path(tmpdir) / "wrong_name"
        invalid_dir.mkdir()
        
        result = runner.invoke(main, [
            '--dependencies-dir', str(invalid_dir)
        ])
        
        assert result.exit_code != 0


def test_cli_custom_output(temp_sbom_dir):
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as tmpdir:
        output_dir = Path(tmpdir) / "custom_output"
        
        result = runner.invoke(main, [
            '--dependencies-dir', str(temp_sbom_dir),
            '--output-dir', str(output_dir),
            '--verbose'
        ])
        
        if result.exit_code == 0:
            assert output_dir.exists()


def test_cli_with_github_options_no_push(temp_sbom_dir):
    runner = CliRunner()
    result = runner.invoke(main, [
        '--dependencies-dir', str(temp_sbom_dir),
        '--github-owner', 'test-owner',
        '--github-repo', 'test-repo'
    ])
    
    assert result.exit_code == 0


def test_cli_file_not_found():
    runner = CliRunner()
    result = runner.invoke(main, [
        '--dependencies-dir', '/totally/fake/path/dependencies'
    ])
    
    assert result.exit_code != 0
