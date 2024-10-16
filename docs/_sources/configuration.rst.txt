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
    :widths: 10 15
    :header-rows: 1

    * - key
      - value 
    * - ``project``
      - a unique project name/id
    * - ``datasets``
      - a list of dataset items.
        
        See `dataset`_.
    * - ``args``
      - `optional` map of arguments per data type to set as default for all files within the project.
        
        Supersedes global ``args``. 



**Note** that the pipeline does not check for the existence of these
metadata within the AnnData object. It is written directly to the Vitessce
config file. If they're incorrectly specified then an error will occur when
Vitessce tries to load the data.
