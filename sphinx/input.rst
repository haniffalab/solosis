.. _official nextflow documentation: https://www.nextflow.io/index.html#GetStarted
.. _official Docker Install guide: https://docs.docker.com/engine/install/
.. _releases on GitHub: https://github.com/haniffalab/solosis
.. _conda: https://docs.conda.io/projects/miniconda/en/latest/
.. _mamba: https://mamba.readthedocs.io/en/latest/mamba-installation.html

.. _input:

Input File
==========

.. _setup_samplefile:


Follow these instructions to populate input files to successfully run the solosis CLI.

Populate Samplefile
-----------

This is the input file can be a comma-separated variable ``.csv`` or tab-separated variable ``.tsv`` file:

- *This input file is an expected input on any command using the* ``--samplefile`` *argument.*

**NOTE:** this input file can include any number of columns, so long as:

- column1 = *sample_id*


.. list-table::
    :widths: 15
    :header-rows: 1

    * - sample_id
    * - pBCN14634207
    * - pBCN14634303
       

.. _setup_cellrangerARC:

Cell RangerARC  
-----------

Cell RangerARC requires a different input file, a ``libraries`` file, which is a *comma-separated variable* ``csv`` file.

- csv file ``libraries.csv`` which includes library type of each sample (e.g. GEX or ATAC)

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


.. _environment_manual:
