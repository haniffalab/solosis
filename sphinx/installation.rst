.. _official nextflow documentation: https://www.nextflow.io/index.html#GetStarted
.. _official Docker Install guide: https://docs.docker.com/engine/install/
.. _releases on GitHub: https://github.com/haniffalab/sc-analysis-nf
.. _conda: https://docs.conda.io/projects/miniconda/en/latest/
.. _mamba: https://mamba.readthedocs.io/en/latest/mamba-installation.html

.. _installation:

Installation
============

Download the sc-analysis-nf Pipeline release. You can look for previous `releases on GitHub`_.

.. code-block:: shell
   :caption: Input

   git clone git@github.com:haniffalab/sc-analysis-nf.git 

.. code-block:: shell
   :caption: Expected Output

   Resolving github.com (github.com)... 140.82.121.3
   Connecting to github.com (github.com)|140.82.121.3|:443... connected.
            ... THIS WILL NEED TO BE CHANGED

Change directory into the new repo.

.. code-block:: shell
   :caption: Input

   cd sc-analysis-nf

.. code-block:: shell
   :caption: Expected Output
    
   sc-analysis-nf/
   sc-analysis-nf/README.md/
   ...
   ...
   sc-analysis-nf/envs/cellrank.yaml
   sc-analysis-nf/input/filtered_gene_bc_matrices/barcodes.tsv

.. _environment:

Environment setup
=================

.. _environment_Docker:

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
   Version:           23.0.4
   API version:       1.42
   Go version:        go1.19.8
   Git commit:        f480fb1
   Built:             Fri Apr 14 10:32:23 2023
   OS/Arch:           linux/amd64
   Context:           default

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

Manual setup
------------

**#1. Check git is installed**

Make sure git 2.17 or later is installed on your computer by using the command:

.. code-block:: shell
   :caption: Input

   git --version

.. code-block:: shell
   :caption: Output

   git version 2.25.1

If Git is missing you will have to follow the `Getting Started Installing Git guide <https://git-scm.com/book/en/v2/Getting-Started-Installing-Git>`__.

**#2. Check java is installed**

Make sure Java 11 or later is installed on your computer by using the command:

.. code-block:: shell
   :caption: Input

   java -version

.. code-block:: shell
   :caption: Output
   
   openjdk version "11.0.18" 2023-01-17
   OpenJDK Runtime Environment (build 11.0.18+10-post-Ubuntu-0ubuntu120.04.1)
   OpenJDK 64-Bit Server VM (build 11.0.18+10-post-Ubuntu-0ubuntu120.04.1, mixed mode, sharing)

If not installed, `download and install Java <https://www.java.com/en/download/manual.jsp>`__.

**#3. Install Nextflow**

Enter the following command in your terminal to install nextflow in the current directory:

.. code-block:: shell
   :caption: Input

   curl -s https://get.nextflow.io | bash
   # Add Nextflow binary to your user's PATH:
   mv nextflow ~/bin/
   # OR system-wide installation:
   # sudo mv nextflow /usr/local/bin

.. code-block:: shell
   :caption: Output
   
   CAPSULE: Downloading dependency org.apache.ivy:ivy:jar:2.5.1
   ...
   CAPSULE: Downloading dependency io.nextflow:nf-commons:jar:23.04.1
                                                                        
         N E X T F L O W
         version 23.04.1 build 5866
         created 15-04-2023 06:51 UTC (07:51 BST)
         cite doi:10.1038/nbt.3820
         http://nextflow.io


   Nextflow installation completed. Please note:
   - the executable file `nextflow` has been created in the folder: ./sc-analysis-nf
   - you may complete the installation by moving it to a directory in your $PATH

You can read more about how to install nextflow in the `official nextflow documentation`_.
