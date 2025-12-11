from click.testing import CliRunner
from sbom_merger.cli import main
import tempfile
from pathlib import Path


def test_cli_help():
    runner = CliRunner()
    result = runner.invoke(main, ['--help'])
    assert result.exit_code == 0
    assert 'dependencies-dir' in result.output


def test_cli_missing_required_arg():
    runner = CliRunner()
    result = runner.invoke(main, [])
    assert result.exit_code != 0


def test_cli_basic_merge(temp_sbom_dir):
    runner = CliRunner()
    result = runner.invoke(main, [
        '--dependencies-dir', str(temp_sbom_dir),
        '--verbose'
    ], catch_exceptions=False)
    
    if result.exit_code != 0:
        print(result.output)
        print(result.exception)
    
    assert result.exit_code == 0
    assert 'Merge completed' in result.output


def test_cli_with_output_dir(temp_sbom_dir):
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as tmpdir:
        output_dir = Path(tmpdir) / "output"
        
        result = runner.invoke(main, [
            '--dependencies-dir', str(temp_sbom_dir),
            '--output-dir', str(output_dir)
        ], catch_exceptions=False)
        
        assert result.exit_code == 0
        assert output_dir.exists()


def test_cli_invalid_dependencies_dir():
    runner = CliRunner()
    result = runner.invoke(main, [
        '--dependencies-dir', '/nonexistent/path/dependencies'
    ])
    assert result.exit_code != 0
    assert 'Error' in result.output
