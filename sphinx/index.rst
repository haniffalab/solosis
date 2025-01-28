|Tests| |Formatting| |Coverage| |DOI|
 
.. |Tests| image:: https://github.com/haniffalab/solosis/actions/workflows/tests-python.yml/badge.svg
   :target: https://github.com/haniffalab/solosis/actions/workflows/tests-python.yml
.. |Formatting| image:: https://github.com/haniffalab/solosis/actions/workflows/precommit.yml/badge.svg
   :target: https://github.com/haniffalab/solosis/actions/workflows/precommit.yml
.. |Coverage| image:: https://codecov.io/github/haniffalab/solosis/graph/badge.svg?token=V80FDINJOD
   :target: https://codecov.io/github/haniffalab/solosis
.. |DOI| image:: https://zenodo.org/badge/DOI/10.5281/zenodo.7405818.svg
   :target: https://doi.org/10.5281/zenodo.7405818

Solosis
=======

CLI tool including common computational utilities for single-cell sequencing data analysis used by the Haniffa Lab. 
This tool is made to work with farm22.

.. toctree::
   :maxdepth: 1
   :caption: Documentation
   :glob:

   setup
   api
   examples

.. toctree::
   :maxdepth: 2
   :hidden:
   :caption: More
  
   input
   output
   development

.. toctree::
   :maxdepth: 2
   :hidden:
   :caption: Project Links
  
   Source Code <https://github.com/haniffalab/solosis>
   Issue Tracker <https://github.com/haniffalab/solosis/issues>


Quick-start
===========
3 initial commands to start using solosis.

1. To use Solosis from the Wellcome Sanger Institute, add the module path.

.. code-block:: shell
   :caption: Input

   module use append /software/cellgen/team298/shared/modulefiles


2. Then load the Solosis module.

.. code-block:: shell
   :caption: Input

   module load solosis


.. code-block:: shell
   :caption: Expected Output

   ** INFO: 'Welcome to Solosis, Module loaded'
   ** INFO: 'Type solosis-cli to get started'

   Loading solosis/0.3.0
      Loading requirement: cellgen/conda /software/modules/ISG/experimental/irods/4.2.11 cellgen/irods


3. Execute the main solosis command to view available tools & commands.

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


