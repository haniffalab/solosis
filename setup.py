from setuptools import find_packages, setup

setup(
    name="solosis",
    version="0.4.1",
    description="A command line interface for working with single-cell data",
    python_requires=">=3.10",
    install_requires=[
        "click",
        "tabulate",
        "pandas",
    ],
    extras_require={
        "dev": [
            "black",
            "colorama",
            "isort",
            "pre-commit",
            "pytest",
            "pytest-cov",
            "pytest-mock",
        ],
        "doc": [
            "Sphinx",
            "sphinx-rtd-theme",
            "sphinx-click",
        ],
    },
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "solosis = solosis.cli:cli",
        ],
    },
)
