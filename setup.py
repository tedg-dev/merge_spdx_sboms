from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="merge-spdx-sboms",
    version="1.0.0",
    author="tedg-dev",
    description="Merge SPDX SBOM dependencies into a comprehensive root SBOM",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tedg-dev/merge_spdx_sboms",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.12",
    install_requires=[
        "click>=8.1.0",
        "spdx-tools>=0.8.0",
        "requests>=2.31.0",
        "pydantic>=2.5.0",
    ],
    entry_points={
        "console_scripts": [
            "merge-spdx-sboms=sbom_merger.cli:main",
        ],
    },
)
