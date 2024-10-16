|Tests| |Sphinx| |Coverage| |DOI|
 
.. |Tests| image:: https://github.com/haniffalab/solosis/actions/workflows/tests-python.yml/badge.svg
   :target: https://github.com/haniffalab/solosis/actions/workflows/tests-python.yml
.. |Sphinx| image:: https://github.com/haniffalab/solosis/actions/workflows/deploy-sphinx.yml/badge.svg
   :target: https://github.com/haniffalab/solosis/actions/workflows/deploy-sphinx.yml
.. |Coverage| image:: https://codecov.io/github/haniffalab/solosis/graph/badge.svg?token=V80FDINJOD
   :target: https://codecov.io/github/haniffalab/solosis
.. |DOI| image:: https://zenodo.org/badge/DOI/10.5281/zenodo.7405818.svg
   :target: https://doi.org/10.5281/zenodo.7405818

Solosis
=================

CLI tool including common computational utilities for single-cell sequencing data analysis used by the Haniffa Lab. 
This tool is made to work with farm22.

**Common computational utilities:**

- `Cellranger`_ A set of analysis pipelines that perform sample demultiplexing, barcode processing, single cell 3' and 5' gene counting, V(D)J transcript sequence assembly and annotation, and Feature Barcode analysis from single cell data.

- `CellrangerARC`_ Cell Ranger ARC is an advanced analytical suite designed for the Chromium Single Cell Multiome ATAC + Gene Expression sequencing.

- `STARsolo`_ a turnkey solution for analyzing droplet single cell RNA sequencing data (e.g. 10X Genomics Chromium).


.. _Cellranger: https://www.10xgenomics.com/support/software/cell-ranger/latest
.. _CellrangerARC: https://www.10xgenomics.com/support/software/cell-ranger-arc/latest
.. _STARsolo: https://github.com/alexdobin/STAR/blob/master/docs/STARsolo.md

.. toctree::
   :maxdepth: 1
   :caption: Documentation
   :glob:

   installation
   configuration
   run
   testing
   visualise

Indices and tables
==================
* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


.. toctree::
   :maxdepth: 2
   :hidden:
   :caption: Project Links
  
   citing
   Source Code <https://github.com/haniffalab/solosis>
   Issue Tracker <https://github.com/haniffalab/solosis/issues>

