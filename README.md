[![python-tests](https://github.com/haniffalab/solosis/actions/workflows/tests-python.yml/badge.svg)](https://github.com/haniffalab/solosis/actions/workflows/tests-python.yml)
[![formatting](https://github.com/haniffalab/solosis/actions/workflows/precommit.yml/badge.svg)](https://github.com/haniffalab/solosis/actions/workflows/precommit.yml)
[![codecov](https://codecov.io/github/haniffalab/solosis/graph/badge.svg?token=V80FDINJOD)](https://codecov.io/github/haniffalab/solosis)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://haniffalab.github.io/solosis)

# Solosis

[![docs](https://img.shields.io/badge/Documentation-online-blue)](https://haniffalab.github.io/solosis)
[![doi](https://zenodo.org/badge/DOI/10.5281/zenodo.13950124.svg)](https://doi.org/10.5281/zenodo.13950124)

A plug and play pipeline for the Haniffa Lab.

## Getting Started

Load the solosis module on Farm:

```sh
module load cellgen/solosis
```

### Tutorials

1. Sphinx [Documentation](https://haniffalab.github.io/solosis) (Python documentation)
2. Notion [Documentation](https://www.notion.so/haniffalab/Solosis-86fec351478140b6b75e375cafccfaaf) (Haniffa Lab users)

# Usage

Execute the CLI:

```sh
solosis-cli
```

```sh
Usage: solosis-cli [OPTIONS] COMMAND [ARGS]...

Options:
--debug  Enable debug mode
--help   Show this message and exit.

Commands:
alignment  Commands for running alignment tools.
history    Commands for managing history.
irods      Commands for working with iRODS.
jobrunner  Farm related commands
scrna      Commands for single-cell RNA-seq tools.
```
