import pytest
from unittest.mock import Mock, patch
from pathlib import Path
import tempfile
from sbom_merger.infrastructure.github_client import GitHubClient


@pytest.fixture
def github_client():
    return GitHubClient("test_token")


def test_github_client_initialization(github_client):
    assert github_client.token == "test_token"
    assert github_client.session.headers['Authorization'] == 'token test_token'


@patch('sbom_merger.infrastructure.github_client.requests.Session')
def test_upload_file_new(mock_session_class, github_client):
    mock_session = Mock()
    mock_session.get.return_value.status_code = 404
    mock_session.put.return_value.status_code = 201
    github_client.session = mock_session
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        f.write('{"test": "data"}')
        temp_file = f.name
    
    try:
        result = github_client.upload_file_to_repo(
            owner="test",
            repo="test-repo",
            file_path=Path(temp_file),
            target_path="test.json"
        )
        assert result is True
    finally:
        Path(temp_file).unlink()


@patch('sbom_merger.infrastructure.github_client.requests.Session')
def test_upload_file_update(mock_session_class, github_client):
    mock_session = Mock()
    mock_session.get.return_value.status_code = 200
    mock_session.get.return_value.json.return_value = {'sha': 'abc123'}
    mock_session.put.return_value.status_code = 200
    github_client.session = mock_session
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        f.write('{"test": "data"}')
        temp_file = f.name
    
    try:
        result = github_client.upload_file_to_repo(
            owner="test",
            repo="test-repo",
            file_path=Path(temp_file),
            target_path="test.json"
        )
        assert result is True
    finally:
        Path(temp_file).unlink()


@patch('sbom_merger.infrastructure.github_client.requests.Session')
def test_upload_file_failure(mock_session_class, github_client):
    mock_session = Mock()
    mock_session.get.return_value.status_code = 404
    mock_session.put.return_value.status_code = 500
    mock_session.put.return_value.text = "Server error"
    github_client.session = mock_session
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        f.write('{"test": "data"}')
        temp_file = f.name
    
    try:
        with pytest.raises(Exception, match="Failed to upload"):
            github_client.upload_file_to_repo(
                owner="test",
                repo="test-repo",
                file_path=Path(temp_file),
                target_path="test.json"
            )
    finally:
        Path(temp_file).unlink()


@patch('sbom_merger.infrastructure.github_client.requests.Session')
def test_update_repository_description(mock_session_class, github_client):
    mock_session = Mock()
    mock_session.patch.return_value.status_code = 200
    github_client.session = mock_session
    
    result = github_client.update_repository_description(
        owner="test",
        repo="test-repo",
        description="Test description"
    )
    assert result is True


@patch('sbom_merger.infrastructure.github_client.requests.Session')
def test_update_repository_description_failure(mock_session_class, github_client):
    mock_session = Mock()
    mock_session.patch.return_value.status_code = 403
    mock_session.patch.return_value.text = "Forbidden"
    github_client.session = mock_session
    
    with pytest.raises(Exception, match="Failed to update"):
        github_client.update_repository_description(
            owner="test",
            repo="test-repo",
            description="Test description"
        )


@patch('sbom_merger.infrastructure.github_client.requests.Session')
def test_create_release(mock_session_class, github_client):
    mock_session = Mock()
    mock_session.post.return_value.status_code = 201
    mock_session.post.return_value.json.return_value = {'id': 123}
    github_client.session = mock_session
    
    result = github_client.create_release(
        owner="test",
        repo="test-repo",
        tag_name="v1.0.0",
        name="Release v1.0.0"
    )
    assert result == {'id': 123}


@patch('sbom_merger.infrastructure.github_client.requests.Session')
def test_create_release_failure(mock_session_class, github_client):
    mock_session = Mock()
    mock_session.post.return_value.status_code = 422
    mock_session.post.return_value.text = "Validation failed"
    github_client.session = mock_session
    
    with pytest.raises(Exception, match="Failed to create release"):
        github_client.create_release(
            owner="test",
            repo="test-repo",
            tag_name="v1.0.0",
            name="Release v1.0.0"
        )
