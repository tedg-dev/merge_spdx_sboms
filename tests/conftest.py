import pytest
from pathlib import Path
import json
import tempfile


@pytest.fixture
def sample_root_sbom():
    return {
        "sbom": {
            "spdxVersion": "SPDX-2.3",
            "dataLicense": "CC0-1.0",
            "SPDXID": "SPDXRef-DOCUMENT",
            "name": "com.github.test/root-project",
            "documentNamespace": "https://spdx.org/spdxdocs/test/root",
            "creationInfo": {
                "creators": ["Tool: test"],
                "created": "2025-12-11T00:00:00Z",
            },
            "packages": [
                {
                    "name": "requests",
                    "SPDXID": "SPDXRef-pypi-requests-abc123",
                    "downloadLocation": "NOASSERTION",
                    "filesAnalyzed": False,
                    "externalRefs": [
                        {
                            "referenceCategory": "PACKAGE-MANAGER",
                            "referenceType": "purl",
                            "referenceLocator": "pkg:pypi/requests",
                        }
                    ],
                },
                {
                    "name": "root-project",
                    "SPDXID": "SPDXRef-root-project",
                    "downloadLocation": "https://github.com/test/root-project",
                    "filesAnalyzed": False,
                },
            ],
            "relationships": [
                {
                    "spdxElementId": "SPDXRef-DOCUMENT",
                    "relatedSpdxElement": "SPDXRef-root-project",
                    "relationshipType": "DESCRIBES",
                },
                {
                    "spdxElementId": "SPDXRef-root-project",
                    "relatedSpdxElement": "SPDXRef-pypi-requests-abc123",
                    "relationshipType": "DEPENDS_ON",
                },
            ],
        }
    }


@pytest.fixture
def sample_dependency_sbom():
    return {
        "sbom": {
            "spdxVersion": "SPDX-2.3",
            "dataLicense": "CC0-1.0",
            "SPDXID": "SPDXRef-DOCUMENT",
            "name": "com.github.psf/requests",
            "documentNamespace": "https://spdx.org/spdxdocs/test/requests",
            "creationInfo": {
                "creators": ["Tool: test"],
                "created": "2025-12-11T00:00:00Z",
            },
            "packages": [
                {
                    "name": "urllib3",
                    "SPDXID": "SPDXRef-pypi-urllib3-def456",
                    "downloadLocation": "NOASSERTION",
                    "filesAnalyzed": False,
                    "versionInfo": "2.0.0",
                    "externalRefs": [
                        {
                            "referenceCategory": "PACKAGE-MANAGER",
                            "referenceType": "purl",
                            "referenceLocator": "pkg:pypi/urllib3@2.0.0",
                        }
                    ],
                },
                {
                    "name": "requests",
                    "SPDXID": "SPDXRef-requests-main",
                    "downloadLocation": "https://github.com/psf/requests",
                    "filesAnalyzed": False,
                },
            ],
            "relationships": [
                {
                    "spdxElementId": "SPDXRef-DOCUMENT",
                    "relatedSpdxElement": "SPDXRef-requests-main",
                    "relationshipType": "DESCRIBES",
                },
                {
                    "spdxElementId": "SPDXRef-requests-main",
                    "relatedSpdxElement": "SPDXRef-pypi-urllib3-def456",
                    "relationshipType": "DEPENDS_ON",
                },
            ],
        }
    }


@pytest.fixture
def temp_sbom_dir(sample_root_sbom, sample_dependency_sbom):
    with tempfile.TemporaryDirectory() as tmpdir:
        base_path = Path(tmpdir)
        project_dir = base_path / "test_user_test_repo"
        deps_dir = project_dir / "dependencies"
        deps_dir.mkdir(parents=True)

        root_path = project_dir / "test_user_test_repo_root.json"
        with open(root_path, "w") as f:
            json.dump(sample_root_sbom, f)

        dep_path = deps_dir / "psf_requests_main.json"
        with open(dep_path, "w") as f:
            json.dump(sample_dependency_sbom, f)

        yield deps_dir
