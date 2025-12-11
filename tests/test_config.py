import pytest
import json
import tempfile
from pathlib import Path
from sbom_merger.infrastructure.config import Config, GitHubAccount


def test_config_load_multi_account():
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump({
            "accounts": [
                {"username": "user1", "token": "token1"},
                {"username": "user2", "token": "token2"}
            ]
        }, f)
        temp_file = f.name
    
    try:
        config = Config(temp_file)
        assert len(config.accounts) == 2
        assert config.accounts[0].username == "user1"
        assert config.accounts[1].token == "token2"
    finally:
        Path(temp_file).unlink()


def test_config_load_legacy_format():
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump({
            "username": "legacy_user",
            "token": "legacy_token"
        }, f)
        temp_file = f.name
    
    try:
        config = Config(temp_file)
        assert len(config.accounts) == 1
        assert config.accounts[0].username == "legacy_user"
    finally:
        Path(temp_file).unlink()


def test_config_get_account():
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump({
            "accounts": [
                {"username": "user1", "token": "token1"},
                {"username": "user2", "token": "token2"}
            ]
        }, f)
        temp_file = f.name
    
    try:
        config = Config(temp_file)
        account = config.get_account("user2")
        assert account is not None
        assert account.username == "user2"
        assert account.token == "token2"
    finally:
        Path(temp_file).unlink()


def test_config_get_account_not_found():
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump({
            "accounts": [{"username": "user1", "token": "token1"}]
        }, f)
        temp_file = f.name
    
    try:
        config = Config(temp_file)
        account = config.get_account("nonexistent")
        assert account is None
    finally:
        Path(temp_file).unlink()


def test_config_get_default_account():
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump({
            "accounts": [{"username": "user1", "token": "token1"}]
        }, f)
        temp_file = f.name
    
    try:
        config = Config(temp_file)
        account = config.get_default_account()
        assert account is not None
        assert account.username == "user1"
    finally:
        Path(temp_file).unlink()


def test_config_invalid_json():
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        f.write("invalid json{}")
        temp_file = f.name
    
    try:
        with pytest.raises(ValueError, match="Invalid keys.json format"):
            Config(temp_file)
    finally:
        Path(temp_file).unlink()


def test_config_no_file():
    config = Config("/nonexistent/keys.json")
    assert len(config.accounts) == 0


def test_config_supported_versions():
    assert Config.is_supported_spdx_version("SPDX-2.3")
    assert not Config.is_supported_spdx_version("SPDX-3.0")


def test_config_supported_formats():
    assert Config.is_supported_output_format("json")
    assert not Config.is_supported_output_format("yaml")
