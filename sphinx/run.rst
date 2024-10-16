.. _run:

Running
=======
 

ADD SOME TYPE OF DESCRIPTION HERE 

**To get started**

.. code-block:: shell
   :caption: Input

   solosis-cli --help

.. code-block:: shell
   :caption: Expected Output
    
   Usage: solosis-cli [OPTIONS] COMMAND [ARGS]...

   Command line utility for the Cellular Genetics programme at the Wellcome
   Sanger Institute

   Options:
   --help  Show this message and exit.

   Commands:
   cellranger      Cellranger aligns sc-rna seq reads...
   cellrangerARC   CellrangerARC aligns GEX & ATAC seq reads...
   pull-fastqs     Downloads processed irods data or any folder from irods...
   pull-processed  Downloads processed irods data or any folder from irods...
   starsolo        STARsolo aligns sc-rna seq reads...

**To run cellranger**

Type ``solosis-cli cellranger --help`` for required inputs 

.. code-block:: shell
   :caption: Input

   solosis-cli cellranger --samplefile path/to/file

.. code-block:: shell
   :caption: Expected Output

   ** See avaiable options using: cellranger -h
   Job <JOBID> is submitted to queue <normal>.

To run cellrangerARC

Type ``solosis-cli cellrangerARC --help`` for required inputs 

.. code-block:: shell
   :caption: Input

   solosis-cli cellrangerARC  --samplefile path/to/file

.. code-block:: shell
   :caption: Expected Output

   ** See avaiable options using: cellranger -h
   Job <JOBID> is submitted to queue <normal>.

**To run STARsolo**

Type ``solosis-cli starsolo --help`` for required inputs 

.. code-block:: shell
   :caption: Input

   solosis-cli starsolo --samplefile path/to/file

.. code-block:: shell
   :caption: Expected Output

   Job <JOBID> is submitted to queue <normal>.

**To pull processed (cellranger) data from iRODS**

Type ``solosis-cli pull-processed --help`` for required inputs 

.. code-block:: shell
   :caption: Input

   solosis-cli pull-processed  --samplefile path/to/file

.. code-block:: shell
   :caption: Expected Output



**To pull sequencing data (fastq) from iRODS**

Type ``solosis-cli pull-fastqs --help`` for required inputs 

.. code-block:: shell
   :caption: Input

   solosis-cli pull-fastqs  --samplefile path/to/file

.. code-block:: shell
   :caption: Expected Output

   Job <JOBID> is submitted to queue <normal>.

Further reading
---------------

For more information about the computational utilities ... `conda <https://www.nextflow.io/docs/latest/conda.html>`__.