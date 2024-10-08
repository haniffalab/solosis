from setuptools import find_packages, setup

setup(
    name="solosis",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "click",
    ],
    entry_points={
        "console_scripts": [
            "solosis = solosis.cli:cli",
        ],
    },
)
