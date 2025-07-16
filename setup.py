"""Setup script for QBench Python SDK."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="qbench-sdk",
    version="0.1.0",
    author="Smithers",
    author_email="nwilliams@smithers.com",
    description="Python SDK for QBench LIMS API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/nwilliams-cts/qbench",
    project_urls={
        "Bug Tracker": "https://github.com/nwilliams-cts/qbench/issues",
        "Documentation": "https://junctionconcepts.zendesk.com/hc/en-us/articles/360030760992-QBench-REST-API-v1-0-Documentation-Full",
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-asyncio>=0.21.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "mypy>=0.950",
            "pre-commit>=2.0.0",
        ],
    },
    include_package_data=True,
    package_data={
        "qbench": ["py.typed"],
    },
)
