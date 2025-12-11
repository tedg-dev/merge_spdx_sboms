import requests
from typing import Optional
from pathlib import Path


class GitHubClient:

    def __init__(self, token: str):
        self.token = token
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json'
        })

    def upload_file_to_repo(
        self,
        owner: str,
        repo: str,
        file_path: Path,
        target_path: str,
        branch: str = "main",
        commit_message: Optional[str] = None
    ) -> bool:
        if not commit_message:
            commit_message = f"Add merged SBOM: {file_path.name}"

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        import base64
        encoded_content = base64.b64encode(content.encode()).decode()

        url = f"https://api.github.com/repos/{owner}/{repo}/contents/{target_path}"

        existing_file = self.session.get(url)
        data = {
            'message': commit_message,
            'content': encoded_content,
            'branch': branch
        }

        if existing_file.status_code == 200:
            data['sha'] = existing_file.json()['sha']

        response = self.session.put(url, json=data)

        if response.status_code in [200, 201]:
            return True
        else:
            raise Exception(
                f"Failed to upload file: {response.status_code} - "
                f"{response.text}"
            )

    def update_repository_description(
        self,
        owner: str,
        repo: str,
        description: str
    ) -> bool:
        url = f"https://api.github.com/repos/{owner}/{repo}"

        data = {
            'description': description
        }

        response = self.session.patch(url, json=data)

        if response.status_code == 200:
            return True
        else:
            raise Exception(
                f"Failed to update repository description: "
                f"{response.status_code} - {response.text}"
            )

    def create_release(
        self,
        owner: str,
        repo: str,
        tag_name: str,
        name: str,
        body: Optional[str] = None
    ) -> dict:
        url = f"https://api.github.com/repos/{owner}/{repo}/releases"

        data = {
            'tag_name': tag_name,
            'name': name,
            'body': body or f"Release {tag_name}",
            'draft': False,
            'prerelease': False
        }

        response = self.session.post(url, json=data)

        if response.status_code == 201:
            return response.json()
        else:
            raise Exception(
                f"Failed to create release: {response.status_code} - "
                f"{response.text}"
            )
