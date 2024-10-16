.. _configuration:

#############
Configuration
#############

Currently, the Solosis CLI can process several types of data files.

**Data files**

* RNA-sequnce R1 & R2 (``.fastq``)
* Multiome GEX & ATAC (``.fastq``)
* Cellranger outputs (``.h5``??)
* Input samplefile ``csv`` or ``txt`` files

=============================================================================================

***************
I am leaving this in for now, so that I canrefer back to this at a later date. 
***************

.. _project:

Project
========

.. code-block:: yaml

  projects:
    - project: project_1
      datasets: 
        ...
      args: 
        h5ad:
          batch_processing: True


Multiple projects can be defined in a single parameters file, and each can define multiple datasets.
Each project item is defined by the following keys:

.. list-table:: 
    :widths: 10 15 10
    :header-rows: 1

    * - sample_id
      - sample_name
      - irods_path
    * - pBCN14634207
      - BK18-BLD-3-SC-1a_G
      - /seq/illumina/runs/48/48776/cellranger/cellranger720_multi_74ed2e8890a887c021241bade6189443
    * - pBCN14634303
      - BK18-BLD-3-SC-1a_C
      - /seq/illumina/runs/48/48776/cellranger/cellranger720_multi_74ed2e8890a887c021241bade6189443
        




