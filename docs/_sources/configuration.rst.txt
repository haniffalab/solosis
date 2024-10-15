.. _configuration:

#############
Configuration
#############

Currently, the sc-analysis-nf pipeline can process several types of data files.

**Data files**

* `AnnData <https://anndata.readthedocs.io/en/latest/>`_ files (``h5ad``)
* Matrix files (``.mtx``) ????
* Gene data in ``csv`` or ``tsv`` files

Running the pipeline requires a YAML parameters file that lists the data to be processed. Templates of this parameters file are available in the `templates directory <https://github.com/haniffalab/sc-analysis-nf/tree/dev/envs/>`__.


.. _parameters_file:

***************
Parameters file
***************

The parameters file defines several configuration options which apply to a full run of the pipeline (which can process one or more datasets). When running the pipeline, the path to the YAML file is indicated through the ``-c`` flag in the command line. For example:

.. code-block:: shell

    nextflow run main.nf -c nextflow.config


A parameters file looks like this:

.. code-block:: yaml

    name: cellrank
    channels:
      - bioconda
      - anaconda
      - conda-forge
      - defaults
    dependencies:
      - anndata=0.9.2
      - anyio=4.1.0
      - appnope=0.1.3
      - asttokens=2.4.1
  
***************
Configuration file
***************
The configuration file defines several paths to certain elements of the pipeline. These in include ``inputs``, ``outputs``\
and ``conda environments``.

A configuration file looks like this:

.. code-block:: java 

    // nextflow.config    
    // nextflow.config

    conda.enabled = true

    // process READ parameters 
    params.read_in = "input/filtered_gene_bc_matrices/hg19/"
    params.read_out = "adata.h5ad"

    // process PREPRO parameters
    params.pre_in = "output/adata.h5ad"
    ...




The YAML file has multiple configuration segements. This is a simple breakdown of the example config file above:

  * The ``//nextflow.config`` entry in the file tells the pipeline the name of the file and to look for this name when looking for a configuration file.

  .. code-block:: java

      //nextflow.config
  
  * The ``conda.enabled`` entry in the file tells the pipeline to utilise conda environments in the process blocks.

  .. code-block:: java

      conda.enabled = true
  
  * The ``params.NAME`` instructs the pipeline to direct the main script to the relative paths of ``input`` and ``outputs`` files.

  .. code-block:: java

      // process READ parameters 
      params.read_in = "input/filtered_gene_bc_matrices/hg19/"
      params.read_out = "adata.h5ad"
      

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
