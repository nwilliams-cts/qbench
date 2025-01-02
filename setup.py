# setup.py
from setuptools import setup, find_packages

setup(
    name="qbench_api",
    version="0.1.3",
    description="Python library for connecting to the QBench API",
    author="Nick Williams, PhD",
    author_email="nwilliams@smithers.com",
    packages=find_packages(),
    install_requires=[
        "requests",
        "PyJWT",
        "aiohttp"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
