from setuptools import find_packages, setup

setup(
    name="solosis",
    version="0.2.2",
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
