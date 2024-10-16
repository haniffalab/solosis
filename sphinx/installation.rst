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

.. _environment:

Environment setup
=================

.. _environment_Docker:

**CURRENTLY NO ENVIRONMENTS TO BE INSTALLED MANUALLY**

Follow these Environment Setup instructions using conda, Docker or manually installing the required components to run sc-analysis-nf.

Using Docker
-----------
**If you have Docker installed locally:**
- Open the Docker application on your device before running the pipeline.
If you want to use Docker, make sure Docker Engine 20.10 or later is installed on your computer by using the command:

.. code-block:: shell
   :caption: Input

   docker version

.. code-block:: shell
   :caption: Output

   Client: Docker Engine - Community
   ...

**If you do not have Docker installed locally:** 
Follow the `official Docker Install guide`_.

.. _environment_conda:

Using conda (optional)
-----------

If you have `conda`_ or `mamba`_ already installed then you can use the ``environment.yaml`` file included in the sc-analysis-nf release to create the environment.

.. code-block:: shell
   :caption: Input

   conda create -n nextflow_env -f environment.yaml

Then make sure you activate the ``environment`` environment before you use the pipeline.

.. code-block:: shell
   :caption: Input

   conda activate environment 


.. _environment_manual:
