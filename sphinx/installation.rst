.. _official nextflow documentation: https://www.nextflow.io/index.html#GetStarted
.. _official Docker Install guide: https://docs.docker.com/engine/install/
.. _releases on GitHub: https://github.com/haniffalab/solosis
.. _conda: https://docs.conda.io/projects/miniconda/en/latest/
.. _mamba: https://mamba.readthedocs.io/en/latest/mamba-installation.html

.. _installation:

Installation
============

Loading the Solosis tool onto Farm22. You can look for previous `releases on GitHub`_.

.. code-block:: shell
   :caption: Input

   module use append /software/cellgen/team298/shared/solosis/modulefiles


Load the solosis module.

.. code-block:: shell
   :caption: Input

   module load solosis


.. code-block:: shell
   :caption: Expected Output
    
   ** INFO: 'Welcome to Solosis, Module loaded'
   ** INFO: 'Type solosis to get started'

   Loading solosis/0.1.0
      Loading requirement: cellgen/conda /software/modules/ISG/experimental/irods/4.2.11
         cellgen/irods 

.. _setup:

Setup
=================

.. _setup_samplefile:


Follow these Setup instructions populate input files to successfully run the solosis CLI.

Populating samplefile
-----------

This is the input file is a text file ``.txt`` and is currently required to exceute the following commands:

- pull-processed 
- Scanpy (notebook)
- merge_h5ad

**NOTE:** this input file can include any number of columns, so long as:

- column1 - *sample_id*
- column2 - *sample_name*
- final column - *irods_path*

.. list-table:: 
    :widths: 10 15 10 10
    :header-rows: 1

    * - sample_id
      - sample_name
      - ...
      - irods_path
    * - pBCN14634207
      - BK18-BLD-3-SC-1a_G
      - ...
      - /seq/illumina/runs/48/48776/cellranger/cellranger720_multi_74ed2e8890a887c021241bade6189443
    * - pBCN14634303
      - BK18-BLD-3-SC-1a_C
      - ...
      - /seq/illumina/runs/48/48776/cellranger/cellranger720_multi_74ed2e8890a887c021241bade6189443
       

.. _setup_cellrangerARC:

CellrangerARC  
-----------

CellrangerARC has two inputs that are required both of which a *comma-separated variable* ``csv`` formatted files.

1. csv file ``libraries.csv`` which includes library type of each sample (e.g. GEX or ATAC)

.. list-table:: 
    :widths: 10 15 10 
    :header-rows: 1

    * - fastqs
      - sample
      - library_type
    * - /lustre/scratch126/cellgen/team298/tmp/HCA_rFSKI14910984
      - HCA_rFSKI14910984
      - Gene Expression
    * - /lustre/scratch126/cellgen/team298/tmp/HCA_rFSKI14910888
      - HCA_rFSKI14910888
      - Chromatin Accessibility    

2. csv file of sample IDs ``samples.csv``

**NOTE: This file is also required when running cellranger, STARsolo and pull-fastqs.**

.. list-table:: 
    :widths: 10 
    :header-rows: 1

    * - samples
    * - HCA_rFSKI14910984
    * - HCA_rFSKI14910888

.. _environment_manual:
