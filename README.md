[![python-tests](https://github.com/haniffalab/solosis/actions/workflows/tests-python.yml/badge.svg)](https://github.com/haniffalab/solosis/actions/workflows/tests-python.yml)
[![formatting](https://github.com/haniffalab/solosis/actions/workflows/precommit.yml/badge.svg)](https://github.com/haniffalab/solosis/actions/workflows/precommit.yml)
[![codecov](https://codecov.io/github/haniffalab/solosis/graph/badge.svg?token=V80FDINJOD)](https://codecov.io/github/haniffalab/solosis)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://haniffalab.github.io/solosis)

# Solosis


<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/haniffalab/solosis">
    <img src="images/haniffa_logo.png" alt="Logo" width="100" height="100">
  </a>

<h1 align="center">solosis</h1>

  <p align="center">
    A plug and play pipeline for the lab - made to work with farm22.
    <br />
    <br />
    <a href="https://github.com/haniffalab/solosis/issues">Report Bug</a>
    &middot;
    <a href="https://github.com/github_username/solosis/issues/new?labels=enhancement&template=feature-request---.md">Request Feature</a>
    <br />
    <br />
    <a href="https://haniffalab.github.io/solosis">
        <img src="https://img.shields.io/badge/Documentation-online-blue" />
    </a>

  </p>
</div>



<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li><a href="#Point-of-Contact">Point of Contact</a></li>
    <li><a href="#Features">Features</a></li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#installation">Installation</a></li>
        <li><a href="#setup">Setup</a></li>
        <li><a href="#Required-Files">Required Files</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
  </ol>
</details>

<!-- Point of contact -->
## Point of Contact:

### Haniffa Lab
Vijay Baskar Mahalingam Shanmugiah- *vm11@sanger.ac.uk*

Dave Horsfall- *dh21@sanger.ac.uk*

Louise Grimble- *lg28@sanger.ac.uk*


<!-- Features -->
## Features 
<div style="border: 1px solid #ccc; padding: 20px; border-radius: 8px; text-align: center;">
  <ol style="display: inline-block; text-align: left;">
    <li><strong>Alignment</strong> – Commands for running alignment tools.</li>
    <li><strong>History</strong> – Commands for managing history.</li>
    <li><strong>Irods</strong> – Commands for working with iRODS.</li>
    <li><strong>Jobrunner</strong> – Farm related commands.</li>
    <li><strong>scrna</strong> – Commands for single-cell RNA-seq tools.</li>
  </ol>
</div>



1. Alignment 
 - cellranger-count (GEX)
 - cellranger-arc-count (GEX & ATAC)
 - cellranger-vdj (Immune profiling BCR/TCR)

2. History
 - view (look up recently executed solosis commands)
 - uid (look up individual executed solosis commands for logs and errors)
 - clear (remove history of executed solosis commands)

3. Irods
 - iget-cellranger ()
 - iget-fastqs (run nf-irods-to-fastq pipeline from CellgenIT to download fastqs onto farm)
 - imeta-report ()

4. Jobrunner
 -

<!-- GETTING STARTED -->
## Getting Started

### Installation
**1. load the solosis module on Farm:**

   ```sh
   module load cellgen/solosis
   ```

<!-- Required Files -->
### Tutorials




<!-- USAGE EXAMPLES -->
# Usage
1. Execute the nextflow pipeline:

    ```sh
    ./solosis-cli
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




# Leaving here for now 

pip-compile --output-file=envs/requirements.txt
pip-compile --extra=dev --output-file=envs/dev-requirements.txt
pip-compile --extra=dev --output-file=envs/doc-requirements.txt

pip-sync envs/requirements.txt
pip-sync envs/dev-requirements.txt
pip-sync envs/doc-requirements.txt
