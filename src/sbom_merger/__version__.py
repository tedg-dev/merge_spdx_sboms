"""Version information for merge-spdx-sboms."""

from pathlib import Path


def _read_version() -> str:
    """Read version from VERSION file or fallback locations."""
    # Try multiple locations for VERSION file
    locations = [
        Path(__file__).parent.parent.parent.parent / "VERSION",  # Development
        Path(__file__).parent.parent.parent / "VERSION",  # Installed in src
        Path(__file__).parent / "VERSION",  # Packaged with module
    ]

    for version_file in locations:
        if version_file.exists():
            return version_file.read_text().strip()

    # Fallback: try to get from package metadata
    try:
        from importlib.metadata import version

        return version("merge-spdx-sboms")
    except Exception:  # nosec B110 - intentional fallback to dev version
        return "0.0.0-dev"


__version__ = _read_version()
__version_info__ = tuple(
    int(x) if x.isdigit() else x for x in __version__.replace("-", ".").split(".")
)
