|Tests| |Sphinx| |Coverage| |DOI|
 
.. |Tests| image:: https://github.com/haniffalab/webatlas-pipeline/actions/workflows/tests-python.yml/badge.svg
   :target: https://github.com/haniffalab/webatlas-pipeline/actions/workflows/tests-python.yml
.. |Sphinx| image:: https://github.com/haniffalab/sc-analysis-nf/actions/workflows/deploy-sphinx.yml/badge.svg
   :target: https://github.com/haniffalab/sc-analysis-nf/actions/workflows/deploy-sphinx.yml
.. |Coverage| image:: https://codecov.io/gh/haniffalab/webatlas-pipeline/branch/main/graph/badge.svg?token=7HQVFH08WJ
   :target: https://app.codecov.io/gh/haniffalab/webatlas-pipeline
.. |DOI| image:: https://zenodo.org/badge/DOI/10.5281/zenodo.7405818.svg
   :target: https://doi.org/10.5281/zenodo.7405818

sc-analysis-nf
=================

This Nextflow pipeline processes single-cell data and carries out an initial QC workflow. 
The pipeline also generates a series of plots uncovering the results of the QC process.

**This QC anaylsis pipeline follows this basic workflow:**
- `SoupX`_ R based tool to remove ambient RNA.
- `scrublet`_ Python-based tool to remove doublets.
- `scanpy`_ python-based tool to analyse sc-RNA seq data (incl. Count transformation, feature selection, dimensionality reduction, batch correction or integration.)


.. _SoupX: https://github.com/constantAmateur/SoupX 
.. _scrublet: https://github.com/swolock/scrublet
.. _scanpy: https://scanpy.readthedocs.io/en/stable/

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
   Source Code <https://github.com/haniffalab/sc-analysis-nf>
   Issue Tracker <https://github.com/haniffalab/sc-analysis-nf/issues>

