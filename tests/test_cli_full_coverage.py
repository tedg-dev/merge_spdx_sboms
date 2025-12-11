from click.testing import CliRunner
from sbom_merger.cli import main
import tempfile
from pathlib import Path
import json
from unittest.mock import patch, Mock


def test_cli_github_push_without_owner(temp_sbom_dir):
    """Test that push to GitHub fails without owner"""
    runner = CliRunner()
    result = runner.invoke(main, [
        '--dependencies-dir', str(temp_sbom_dir),
        '--push-to-github'
    ])
    
    assert result.exit_code != 0
    assert 'github-owner' in result.output or 'required' in result.output


def test_cli_github_push_without_repo(temp_sbom_dir):
    """Test that push to GitHub fails without repo"""
    runner = CliRunner()
    result = runner.invoke(main, [
        '--dependencies-dir', str(temp_sbom_dir),
        '--push-to-github',
        '--github-owner', 'test-owner'
    ])
    
    assert result.exit_code != 0


@patch('sbom_merger.cli.GitHubClient')
@patch('sbom_merger.cli.Config')
def test_cli_github_push_success(mock_config, mock_github_client, temp_sbom_dir):
    """Test successful GitHub push"""
    # Setup mocks
    mock_account = Mock()
    mock_account.token = 'test_token'
    mock_config_instance = Mock()
    mock_config_instance.get_account.return_value = mock_account
    mock_config_instance.get_default_account.return_value = mock_account
    mock_config.return_value = mock_config_instance
    
    mock_client_instance = Mock()
    mock_client_instance.upload_file_to_repo.return_value = True
    mock_github_client.return_value = mock_client_instance
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump({"accounts": [{"username": "test", "token": "token"}]}, f)
        key_file = f.name
    
    try:
        runner = CliRunner()
        result = runner.invoke(main, [
            '--dependencies-dir', str(temp_sbom_dir),
            '--key-file', key_file,
            '--push-to-github',
            '--github-owner', 'test-owner',
            '--github-repo', 'test-repo'
        ])
        
        assert result.exit_code == 0 or 'Pushed' in result.output
    finally:
        Path(key_file).unlink()


def test_cli_no_config_file_no_push(temp_sbom_dir):
    """Test CLI works without keys.json when not pushing"""
    runner = CliRunner()
    result = runner.invoke(main, [
        '--dependencies-dir', str(temp_sbom_dir),
        '--key-file', '/nonexistent/keys.json'
    ])
    
    # Should succeed because we're not pushing to GitHub
    assert result.exit_code == 0


@patch('sbom_merger.cli.GitHubClient')
def test_cli_github_push_error(mock_github_client, temp_sbom_dir):
    """Test GitHub push error handling"""
    mock_client_instance = Mock()
    mock_client_instance.upload_file_to_repo.side_effect = Exception("Upload failed")
    mock_github_client.return_value = mock_client_instance
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump({"accounts": [{"username": "test", "token": "token"}]}, f)
        key_file = f.name
    
    try:
        runner = CliRunner()
        result = runner.invoke(main, [
            '--dependencies-dir', str(temp_sbom_dir),
            '--key-file', key_file,
            '--push-to-github',
            '--github-owner', 'test-owner',
            '--github-repo', 'test-repo'
        ])
        
        # Should handle error gracefully
        assert 'Error' in result.output or result.exit_code != 0
    finally:
        Path(key_file).unlink()


def test_cli_with_account_option(temp_sbom_dir):
    """Test CLI with account selection"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump({
            "accounts": [
                {"username": "account1", "token": "token1"},
                {"username": "account2", "token": "token2"}
            ]
        }, f)
        key_file = f.name
    
    try:
        runner = CliRunner()
        result = runner.invoke(main, [
            '--dependencies-dir', str(temp_sbom_dir),
            '--key-file', key_file,
            '--account', 'account2'
        ])
        
        assert result.exit_code == 0
    finally:
        Path(key_file).unlink()


def test_cli_all_options(temp_sbom_dir):
    """Test CLI with all non-GitHub options"""
    with tempfile.TemporaryDirectory() as tmpdir:
        output_dir = Path(tmpdir) / "output"
        key_file = Path(tmpdir) / "keys.json"
        key_file.write_text(json.dumps({"accounts": [{"username": "test", "token": "token"}]}))
        
        runner = CliRunner()
        result = runner.invoke(main, [
            '--dependencies-dir', str(temp_sbom_dir),
            '--output-dir', str(output_dir),
            '--key-file', str(key_file),
            '--account', 'test',
            '--verbose'
        ])
        
        assert result.exit_code == 0
