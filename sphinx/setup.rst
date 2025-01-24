.. _installation:

Setup
=====

To use Solosis from the Wellcome Sanger Institute, add the module path

.. code-block:: shell
   :caption: Input

   module use append /software/cellgen/team298/shared/modulefiles

Then load the Solosis module

.. code-block:: shell
   :caption: Input

   module load solosis

.. admonition:: Working with iRODS

   If you're running commands that work with iRODS, please load the module and authenticate yourself.

   .. code-block:: shell

      module load cellgen/irods
      iinit 
