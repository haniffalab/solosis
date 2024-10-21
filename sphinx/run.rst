.. _run:

Run
=======

The solosis command-line tool requires very few commands to achieve many data analysis processes.
Getting started is simple, see below:

Getting started
---------------

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

Cellranger execution
---------------

To run cellranger, execute the following command:

**Note:** Type ``solosis-cli cellranger --help`` for required inputs and addition parameters. 

.. code-block:: shell
   :caption: Input

   solosis-cli cellranger --samplefile path/to/file

.. code-block:: shell
   :caption: Expected Output

   ** See avaiable options using: cellranger -h
   Job <JOBID> is submitted to queue <normal>.

After the job <JOBID> has been submitted to the queue <NORMAL> , you can check the status of the queue 
using ``bjobs`` command. This can be a quick way to identify whether you have populated the input
files correctly, as well as, check whether job are actively running (RUN) or in the queue (PEND).

Command results will be found at ``/lustre/scratch126/cellgen/team298/sample_data/SAMPLE_ID/cellranger-hl``

CellrangerARC execution
---------------

To run cellrangerARC, execute the following command:

**Note:** Type ``solosis-cli cellrangerARC --help`` for required inputs and addition parameters. 

.. code-block:: shell
   :caption: Input

   solosis-cli cellrangerARC  --samplefile path/to/file

.. code-block:: shell
   :caption: Expected Output

   ** See avaiable options using: cellranger -h
   Job <JOBID> is submitted to queue <normal>.

After the job <JOBID> has been submitted to the queue <NORMAL> , you can check the status of the queue 
using ``bjobs`` command. This can be a quick way to identify whether you have populated the input
files correctly, as well as, check whether job are actively running (RUN) or in the queue (PEND).

Command results will be found at ``/lustre/scratch126/cellgen/team298/sample_data/SAMPLE_ID/cellrangerARC-hl``

STARsolo execution
---------------

To run STARsolo, execute the following command:

**Note:** Type ``solosis-cli starsolo --help`` for required inputs and addition parameters. 

.. code-block:: shell
   :caption: Input

   solosis-cli starsolo --samplefile path/to/file

.. code-block:: shell
   :caption: Expected Output

   Job <JOBID> is submitted to queue <normal>.

After the job <JOBID> has been submitted to the queue <NORMAL> , you can check the status of the queue 
using ``bjobs`` command. This can be a quick way to identify whether you have populated the input
files correctly, as well as, check whether job are actively running (RUN) or in the queue (PEND).

Command results will be found at ``/lustre/scratch126/cellgen/team298/sample_data/SAMPLE_ID/starsolo-hl``

Pull cellranger outputs (irods)
---------------

To pull processed (cellranger) data from iRODS, execute the following command:

**Note:** Type ``solosis-cli pull-processed --help`` for required inputs and addition parameters. 
 
.. code-block:: shell
   :caption: Input

   solosis-cli pull-processed  --samplefile path/to/file

.. code-block:: shell
   :caption: Expected Output

After the job <JOBID> has been submitted to the queue <NORMAL> , you can check the status of the queue 
using ``bjobs`` command. This can be a quick way to identify whether you have populated the input
files correctly, as well as, check whether job are actively running (RUN) or in the queue (PEND).

Command results will be found at ``/lustre/scratch126/cellgen/team298/sample_data/SAMPLE_ID/pulled-processed`` 
and will also be sym-linked to the execution directory (where you executed the command).

Pull fastqs (irods)
---------------

To pull sequencing data (fastq) from iRODS, execute the following command:

**Note:** Type ``solosis-cli pull-fastqs --help`` for required inputs and addition parameters. 

.. code-block:: shell
   :caption: Input

   solosis-cli pull-fastqs  --samplefile path/to/file

.. code-block:: shell
   :caption: Expected Output

   Job <JOBID> is submitted to queue <normal>.

After the job <JOBID> has been submitted to the queue <NORMAL> , you can check the status of the queue 
using ``bjobs`` command. This can be a quick way to identify whether you have populated the input
files correctly, as well as, check whether job are actively running (RUN) or in the queue (PEND).

Command results will be found at ``/lustre/scratch126/cellgen/team298/tmp/SAMPLE_ID``

**NOTE: all samples will be removed from this tmp/ dir after 60 days**

Cellbender
---------------

To run cellbender to remove RNA artifacts, execute the following command:

**Note:** Type ``solosis-cli cellbender --help`` for required inputs and addition parameters. 

.. code-block:: shell
   :caption: Input

   solosis-cli cellbender --samplefile path/to/file.txt --total_droplets_included VALUE

.. code-block:: shell
   :caption: Expected Output

   Job <JOBID> is submitted to queue <normal>.

After the job <JOBID> has been submitted to the queue <NORMAL> , you can check the status of the queue 
using ``bjobs`` command. This can be a quick way to identify whether you have populated the input
files correctly, as well as, check whether job are actively running (RUN) or in the queue (PEND).

Scanpy Workflow
---------------

To run a basic scanpy workflow and generate a .ipynb, execute the following command:

**Note:** Type ``solosis-cli scanpy --help`` for required inputs and addition parameters. 

.. code-block:: shell
   :caption: Input

   solosis-cli scanpy  --samplefile path/to/file.txt

.. code-block:: shell
   :caption: Expected Output

   Job <JOBID> is submitted to queue <normal>.

After the job <JOBID> has been submitted to the queue <NORMAL> , you can check the status of the queue 
using ``bjobs`` command. This can be a quick way to identify whether you have populated the input
files correctly, as well as, check whether job are actively running (RUN) or in the queue (PEND).

Merge h5ad Objects
---------------

To pull merge h5ad objects together, execute the following command:

**Note:** Type ``solosis-cli merge-h5ad --help`` for required inputs and addition parameters. 

.. code-block:: shell
   :caption: Input

   solosis-cli merge-h5ad  --samplefile path/to/file.txt --merged_filename example-merge.h5ad

.. code-block:: shell
   :caption: Expected Output

   Job <JOBID> is submitted to queue <normal>.

After the job <JOBID> has been submitted to the queue <NORMAL> , you can check the status of the queue 
using ``bjobs`` command. This can be a quick way to identify whether you have populated the input
files correctly, as well as, check whether job are actively running (RUN) or in the queue (PEND).

Further reading
---------------

For more information about the computational utilities ... `insert link to index.rst` 