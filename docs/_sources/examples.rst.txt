.. _examples:

Examples
========


.. code-block:: shell
   :caption: Input

   solosis-cli


.. code-block:: shell
   :caption: Expected Output

   Usage: solosis-cli [OPTIONS] COMMAND [ARGS]...

    Command line utility for the Cellular Genetics programme at the Wellcome
    Sanger Institute

   Options:
    --version  Show the version and exit.
    --help     Show this message and exit.

   Commands:
    alignment   Commands for running alignment tools.
    filesystem  Commands for file and directory operations.
    irods       Commands for working with iRODS.
    ncl-bsu     Commands for Newcastle University BSU.
    sc-rna      Commands for single-cell RNA-seq workflows.


**Alignment**

Cell Ranger ARC example using `--sample`

.. code-block:: shell
   :caption: Input

   solosis-cli alignment cellranger-arc --sample HCA_rFSKI14910984 --libraries /lustre/scratch126/cellgen/team298/lg28/irods_test/libARC.csv 


.. code-block:: shell
   :caption: Expected Output

      SOLOSIS    ~  version 0.3.0
    [info] Starting Process: cellranger-arc
    Job <192355> is submitted to queue <normal>.

Cell Ranger ARC example using `--samplefile`

.. code-block:: shell
   :caption: Input

   solosis-cli alignment cellranger-arc --samplefile /lustre/scratch126/cellgen/team298/lg28/irods_test/ARC.csv --libraries /lustre/scratch126/cellgen/team298/lg28/irods_test/libARC.csv


.. code-block:: shell
    :caption: Expected Output

      SOLOSIS    ~  version 0.3.0
    [info] Starting Process: cellranger-arc
    Job <192355> is submitted to queue <normal>.


Cell Ranger count example using `--sample`

.. code-block:: shell
   :caption: Input

   solosis-cli alignment cellranger-count --sample HCA_SkO14189565


.. code-block:: shell
   :caption: Expected Output

      SOLOSIS    ~  version 0.3.0
    [info] Starting Process: cellranger-count
    [info] loading Cell Ranger version 7.2.0
    [action] executing command: /nfs/users/nfs_l/lg28/repos/solosis/bin/alignment/cellranger-count/submit.sh HCA_SkO14542036 7.2.0 --no-bam
    [progress] starting Cell Ranger for samples: HCA_SkO14542036...
    [progress] Cell Ranger submitted successfully:
    ** See avaiable options using: cellranger -h
    Job <199964> is submitted to queue <normal>.

    [success] cellranger submission complete. run `bjobs -w`  for progress.


Cell Ranger count example using `--samplefile `

.. code-block:: shell
   :caption: Input

   solosis-cli alignment cellranger-count --samplefile /lustre/scratch126/cellgen/team298/lg28/irods_test/sol_input.csv


.. code-block:: shell
   :caption: Expected Output

      SOLOSIS    ~  version 0.3.0
    [info] Starting Process: cellranger-count
    [info] loading Cell Ranger version 7.2.0
    [action] executing command: /nfs/users/nfs_l/lg28/repos/solosis/bin/alignment/cellranger-count/submit.sh HCA_SkO14542035,HCA_SkO14542036 7.2.0 --no-bam
    [progress] starting Cell Ranger for samples: HCA_SkO14542035,HCA_SkO14542036...
    [progress] Cell Ranger submitted successfully:
    ** See avaiable options using: cellranger -h
    Job <201312> is submitted to queue <normal>.

    [success] cellranger submission complete. run `bjobs -w`  for progress.


STARsolo example using `--samplefile`

.. code-block:: shell
   :caption: Input

   solosis-cli alignment starsolo --samplefile /lustre/scratch126/cellgen/team298/lg28/irods_test/sol_input.csv


.. code-block:: shell
   :caption: Expected Output

     SOLOSIS    ~  version 0.3.0
    [info] Starting Process: starsolo
    [info] loading starsolo
    [action] executing command: /nfs/users/nfs_l/lg28/repos/solosis/bin/alignment/starsolo/submit.sh HCA_SkO14542035,HCA_SkO14542036
    [progress] starting starsolo for samples: HCA_SkO14542035,HCA_SkO14542036...
    [progress] starsolo submitted successfully:
    Job <201433> is submitted to queue <normal>.
    Submitted array LSF job for 2 samples.

    [success] starsolo submission complete. run `bjobs -w`  for progress.


**Filesystem**

Disk-usage example 

.. code-block:: shell
   :caption: Input

   solosis-cli filesystem disk-usage


.. code-block:: shell
   :caption: Expected Output

     SOLOSIS    ~  version 0.3.0
    [info] Starting Process: disk-usage
    [progress] Calculating disk usage for team298 ...
    [progress] 
    workspace    size   used     avail  use%  
    ---------    -----  ------   -----  ----- 
    Lustre       45T    41.03T   4T     91%   
    nfs          60T    49T      12T    81%   
    warehouse    1.0T   769G     256G   76%


File-count example 

.. code-block:: shell
   :caption: Input

   solosis-cli filesystem file-count


.. code-block:: shell
   :caption: Expected Output

      SOLOSIS    ~  version 0.3.0
    [info] Launching: filecount
    [progress] 
    Script completed. Email sent to lg28@sanger.ac.uk


**irods**

iget-cellranger example using `--samplefile`

.. code-block:: shell
   :caption: Input

   solosis-cli irods iget-cellranger --samplefile /lustre/scratch126/cellgen/team298/lg28/irods_test/sol_input.csv


.. code-block:: shell
   :caption: Expected Output

      SOLOSIS    ~  version 0.3.0
    [info] Starting Process: iget-cellranger
    [success] Command executed successfully.
    [info] Samples for download:
    1. HCA_SkO14542035
    2. HCA_SkO14542036
    [success] LSF Job ID 202652 submitted to 'small' queue.
    [info] Use `bjobs` to monitor job completion.
    [info] View job logs at $HOME/logs.


iget-fastqs example using `--samplefile`

.. code-block:: shell
   :caption: Input

    solosis-cli irods iget-fastqs --samplefile /lustre/scratch126/cellgen/team298/lg28/irods_test/sol_input.csv


.. code-block:: shell
   :caption: Expected Output

      SOLOSIS    ~  version 0.3.0
    [info] Starting Process: iget-fastqs
    [success] Command executed successfully.
    [progress] samples without FASTQ files: ['HCA_SkO14542035', 'HCA_SkO14542036']
    [progress] executing command: /nfs/users/nfs_l/lg28/repos/solosis/bin/irods/iget-fastqs/submit.sh HCA_SkO14542035,HCA_SkO14542036
    [progress] starting process for samples: HCA_SkO14542035,HCA_SkO14542036...
    \ #*spinner*


**sc-rna**

cellbender example using `--samplefile`

.. code-block:: shell
   :caption: Input

   solosis-cli sc-rna cellbender --samplefile /lustre/scratch126/cellgen/team298/lg28/irods_test/sol_input.csv --total_droplets_included 30000


.. code-block:: shell
   :caption: Expected Output

      SOLOSIS    ~  version 0.3.0osis$ 
    ** See avaiable options using: cellbender remove-background -h
    ** Using custom python for this environment
    python=3.10.12 cellbender=0.3.0 torch=2.3.1
    Job <203560> is submitted to queue <gpu-normal>.



merge-h5ad example using `--samplefile`

.. code-block:: shell
   :caption: Input

    solosis-cli sc-rna merge-h5ad --samplefile /lustre/scratch126/cellgen/team298/lg28/irods_test/sol_input.csv --merged_filename merged.h5ad


.. code-block:: shell
   :caption: Expected Output

      SOLOSIS    ~  version 0.3.0
    Your run token is: 
    Generating a bsub script rna_merge_.bsub
    Job <205162> is submitted to default queue <normal>.

scanpy example using `--samplefile`

.. code-block:: shell
   :caption: Input

   solosis-cli sc-rna scanpy --samplefile /lustre/scratch126/cellgen/team298/lg28/irods_test/sol_input.csv 


.. code-block:: shell
   :caption: Expected Output

      SOLOSIS    ~  version 0.3.0
    (2) [Info] _HCA_SkO14542035 will be processed in /lustre/scratch126/cellgen/team298/sample_data//_HCA_SkO14542035/rna_scanpy/
    (3) [Info] _HCA_SkO14542036 will be processed in /lustre/scratch126/cellgen/team298/sample_data//_HCA_SkO14542036/rna_scanpy/
    [Info] batch job submitted. check using 'bjobs -w' command
    Job <205522> is submitted to default queue <normal>.