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



**Environment Variables**

Then load environment variables 

.. code-block:: shell
   :caption: Input

   export TEAM_SAMPLE_DATA_DIR=/lustre/scratch126/cellgen/team298/data/samples



**iRODS**

For commands using irods, Load the irods module 

.. code-block:: shell
   :caption: Input

   module load cellgen/irods


Then log into irods

.. code-block:: shell
   :caption: Input

   iinit 
