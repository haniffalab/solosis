.. _development:

.. _pytest: https://docs.pytest.org/en/7.1.x/

Development
===========

If you are developing or want to contribute to Solosis, please read this page.

1. **Log-in to Farm**


2. **If you haven't already, create a directory for your Git repository in your home directory.**

Ensure you are in your home directory 
::

    pwd


.. code-block:: shell
   :caption: Expected Output

   /nfs/users/nfs_l/<USER>

Then create the directory 
::

    mkdir repos 
    cd repos/


3. **Clone the solosis git repository**

::

    git clone git@github.com:haniffalab/solosis.git
    cd solosis

4. **Export environment variables** 

::

    export export LSB_DEFAULT_USERGROUP=<USERGROUP>
    export TEAM_DATA_DIR=/lustre/scratch124/cellgen/haniffa/data
    export TEAM_LOGS_DIR=/lustre/scratch124/cellgen/haniffa/logs

5. **Set-up new git branch**

Check which branch you're currently in
::

    git status 

.. code-block:: shell
   :caption: Expected Output

   On branch dev
   Your branch is up-to-date with 'origin/dev'.


Move to dev branch 

::

    git checkout dev 


Create a new branch (off dev branch) to begin contributing. More info `here <https://www.atlassian.com/git/tutorials/using-branches/git-checkout#:~:text=New%20branches,to%20switch%20to%20that%20branch>`_

::

    git checkout -b ＜new-branch＞


For information on Naming nomenclature of git branches view this `page <https://medium.com/@abhay.pixolo/naming-conventions-for-git-branches-a-cheatsheet-8549feca2534>`_

6. **Executing solosis commands**

Executing solosis commands while developing need to solosis-cli to be as follows:
::

    ./solosis-cli



7. **Committing changes to dev branch**

Run the following commands:
::

    git add .
    git commit -m "ADD MESSAGE HERE"
    git push 

Once changes are complete, create `Pull Request <https://github.com/haniffalab/solosis/pulls>`_ to merge changes to dev.

.. _Pull Request: <https://github.com/haniffalab/solosis/pulls>


pytest
===========
Create and activate the virtual environment

::

    python -m venv .venv
    source .venv/bin/activate

Install dev dependencies and install pre-commit hooks

::

    pip install --upgrade pip
    python -m pip install -r envs/requirements.txt
    python -m pip install -r envs/dev-requirements.txt
    python -m pip install -r envs/doc-requirements.txt
    pre-commit install
    
Run Solosis in development mode

::

    python -m solosis.cli

The pre-commit config includes ``black`` formatting and ``isort`` are implemented.
You can manually check ``black`` formatting and ``isort`` as follows:

::

    black path/to/file.py
    isort path/to/file.py

Python testing
--------------

Set the :code:`PYTHONPATH` environment variable to the :code:`bin` directory where the scripts are stored, and then run the following command:

::

    python -m pytest -q tests/test_cli.py



