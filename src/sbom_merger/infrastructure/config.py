import json
from pathlib import Path
from typing import Optional, List, Dict
from dataclasses import dataclass


@dataclass
class GitHubAccount:
    username: str
    token: str


class Config:
    SUPPORTED_SPDX_VERSIONS = ["SPDX-2.3"]
    FUTURE_SPDX_VERSIONS = ["SPDX-3.0", "SPDX-3.0.1"]
    
    SUPPORTED_OUTPUT_FORMATS = ["json"]
    FUTURE_OUTPUT_FORMATS = ["yaml", "rdf"]
    
    def __init__(self, key_file: Optional[str] = None):
        self.key_file = key_file or "keys.json"
        self.accounts: List[GitHubAccount] = []
        self._load_accounts()
    
    def _load_accounts(self) -> None:
        key_path = Path(self.key_file)
        if not key_path.exists():
            return
        
        try:
            with open(key_path, 'r') as f:
                data = json.load(f)
            
            if "accounts" in data:
                for account_data in data["accounts"]:
                    self.accounts.append(
                        GitHubAccount(
                            username=account_data["username"],
                            token=account_data["token"]
                        )
                    )
            elif "username" in data and "token" in data:
                self.accounts.append(
                    GitHubAccount(
                        username=data["username"],
                        token=data["token"]
                    )
                )
        except (json.JSONDecodeError, KeyError) as e:
            raise ValueError(f"Invalid keys.json format: {e}")
    
    def get_account(self, username: str) -> Optional[GitHubAccount]:
        for account in self.accounts:
            if account.username == username:
                return account
        return None
    
    def get_default_account(self) -> Optional[GitHubAccount]:
        return self.accounts[0] if self.accounts else None
    
    @staticmethod
    def is_supported_spdx_version(version: str) -> bool:
        return version in Config.SUPPORTED_SPDX_VERSIONS
    
    @staticmethod
    def is_supported_output_format(fmt: str) -> bool:
        return fmt in Config.SUPPORTED_OUTPUT_FORMATS
