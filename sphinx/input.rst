.. _official nextflow documentation: https://www.nextflow.io/index.html#GetStarted
.. _official Docker Install guide: https://docs.docker.com/engine/install/
.. _releases on GitHub: https://github.com/haniffalab/solosis
.. _conda: https://docs.conda.io/projects/miniconda/en/latest/
.. _mamba: https://mamba.readthedocs.io/en/latest/mamba-installation.html

.. _input:

Input Data
==========

Follow these instructions to populate input files to successfully run the solosis CLI.

Samplefile
----------

Several commands in Solosis accept a ``--samplefile`` option where you can pass multiple samples as a comma-separated ``.csv`` or tab-separated ``.tsv`` file. The column that contains the Sample IDs would be called "sample_id".

.. list-table::
    :header-rows: 1

    * - sample_id
    * - s12345
    * - s67890       

.. _setup_cellrangerARC:

Cell Ranger ARC Libraries File
------------------------------

Cell Ranger ARC requires a specific input file, called a ``libraries`` file, which is a *comma-separated variable* ``csv`` file. Construct a 3-column libraries CSV file that specifies the location of the ATAC and GEX FASTQ files associated with the sample. For example:

.. list-table:: 
    :header-rows: 1

    * - fastqs
      - sample
      - library_type
    * - /home/jdoe/runs/HNGEXSQXXX/outs/fastq_path
      - s12345
      - Gene Expression
    * - /home/jdoe/runs/HNATACSQXX/outs/fastq_path
      - s67890
      - Chromatin Accessibility    

