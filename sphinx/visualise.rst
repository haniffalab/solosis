.. _visualise:

Visualising
===========


**Common computational utilities:**

- `Cellranger`_ A set of analysis pipelines that perform sample demultiplexing, barcode processing, single cell 3' and 5' gene counting, V(D)J transcript sequence assembly and annotation, and Feature Barcode analysis from single cell data.

- `CellrangerARC`_ Cell Ranger ARC is an advanced analytical suite designed for the Chromium Single Cell Multiome ATAC + Gene Expression sequencing.

- `STARsolo`_ a turnkey solution for analyzing droplet single cell RNA sequencing data (e.g. 10X Genomics Chromium).


.. _Cellranger: https://www.10xgenomics.com/support/software/cell-ranger/latest
.. _CellrangerARC: https://www.10xgenomics.com/support/software/cell-ranger-arc/latest
.. _STARsolo: https://github.com/alexdobin/STAR/blob/master/docs/STARsolo.md

The module generates a number of outputs, these are mainly intermediate files that allow 
for further data analysis within solosis and beyond.

Would like to add to tree diagram of farm /lustre output dirs

.. code-block:: shell

    /lustre/.../team298/
    |
    |-- sample_data
    |   L__ SAMPLE_ID
    |       L__ cellrangerARC
    |       L__ cellranger-hl
    |       L__ starsolo-hl
    |       L__ processed_sanger
    |       L__ rna_scanpy
    |       
    |-- tmp
    |   L__ SAMPLE_ID
    |       L__ SAMPLE_ID_R1.fastq
    |       L__ SAMPLE_ID_R2.fastq
