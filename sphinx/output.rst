.. _output:

Output Data
===========

**Solosis CLI generates a number different types of of outputs.**


The commands listed below generate outputs in a common place:

- cellranger-count
- cellranger-arc
- starsolo
- iget-fastqs
- iget-cellranger
- cellbender


The outputs for these commands will be found here: 

.. code-block:: shell

    /lustre/scratch126/cellgen/team298/data/samples/


The output file should reflect the tool or command that was executed by solosis, like so:

.. code-block:: shell
    :caption: Tree Diagram of some expected output files on Farm 

    /lustre/scratch126/cellgen/team298/data/samples/
    │       └── cellranger-arc/
    |       ├── SAMPLE_ID/
    │           ├── cellranger/
    │           ├── fastq/
    │           ├── starsolo/
    │           ├── cellbender/
    |           └── ...


**Cell Ranger ARC**

Cell Ranger ARC outputs will be found here:

.. code-block:: shell

    /lustre/scratch126/cellgen/team298/data/cellranger-arc/


.. code-block:: shell
    :caption: Tree Diagram of Cell Ranger ARC outputs on Farm

    /lustre/scratch126/cellgen/team298/data/cellranger-arc/
    │       └── SAMPLE_ID/
    │           ├── outs/


**Logs** 

STDOUT and STDERR for commands executed will be found here:

.. code-block:: shell

    $HOME/logs


