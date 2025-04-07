[![python-tests](https://github.com/haniffalab/solosis/actions/workflows/tests-python.yml/badge.svg)](https://github.com/haniffalab/solosis/actions/workflows/tests-python.yml)
[![formatting](https://github.com/haniffalab/solosis/actions/workflows/precommit.yml/badge.svg)](https://github.com/haniffalab/solosis/actions/workflows/precommit.yml)
[![codecov](https://codecov.io/github/haniffalab/solosis/graph/badge.svg?token=V80FDINJOD)](https://codecov.io/github/haniffalab/solosis)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://haniffalab.github.io/solosis)

# Solosis

[![docs](https://img.shields.io/badge/Documentation-online-blue)](https://haniffalab.github.io/solosis)
[![doi](https://zenodo.org/badge/DOI/10.5281/zenodo.13950124.svg)](https://doi.org/10.5281/zenodo.13950124)

A plug and play pipeline for the lab
This suite is made to work with farm22. The instructions below are to be performed in farm unless otherwise stated.

# Setup

```
module load solosis
solosis-cli --help
```

pip-compile --output-file=envs/requirements.txt
pip-compile --extra=dev --output-file=envs/dev-requirements.txt
pip-compile --extra=dev --output-file=envs/doc-requirements.txt

pip-sync envs/requirements.txt
pip-sync envs/dev-requirements.txt
pip-sync envs/doc-requirements.txt
