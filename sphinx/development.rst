.. _development:

.. _pytest: https://docs.pytest.org/en/7.1.x/

Development
===========

If you are developing or contributing to Solosis, follow the steps below to set up your local development environment.

git
***

**Clone the Solosis Git repository**

::

    git clone git@github.com:haniffalab/solosis.git
    cd solosis

**Export required environment variables**

Replace placeholders with values specific to your environment:

::

    export LSB_DEFAULT_USERGROUP=<USERGROUP>
    export TEAM_DATA_DIR=<DATA_DIR>
    export TEAM_LOGS_DIR=<LOG_DIR>

Environment
***********

**Create and activate a virtual environment**

::

    python -m venv .venv
    source .venv/bin/activate

**Install dependencies and pre-commit hooks**

::

    pip install --upgrade pip
    python -m pip install -r envs/requirements.txt
    python -m pip install -r envs/dev-requirements.txt
    python -m pip install -r envs/doc-requirements.txt
    pre-commit install

The pre-commit configuration includes checks for code formatting using ``black`` and import ordering using ``isort``.  
You can run these manually as follows:

::

    black path/to/file.py
    isort path/to/file.py

Branches
********

**Check your current branch**

::

    git status


.. code-block:: shell
   :caption: Expected output

   On branch main
   Your branch is up-to-date with 'origin/main'.

**Switch to the `dev` branch**

::

    git checkout dev

**Create a new branch from `dev`**

::

    git checkout -b <new-branch>

For more information on branching, see:
- `Git checkout guide <https://www.atlassian.com/git/tutorials/using-branches/git-checkout>`_
- `Branch naming conventions <https://medium.com/@abhay.pixolo/naming-conventions-for-git-branches-a-cheatsheet-8549feca2534>`_

Executing Solosis
*****************

When developing, run Solosis as follows:

::

    python -m solosis.cli

Committing Changes
******************

**Commit and push your changes**

::

    git add .
    git commit -m "ADD MESSAGE HERE"
    git push

Once changes are ready, create a `Pull Request <https://github.com/haniffalab/solosis/pulls>`_ to merge them into ``dev``.

pip-compile
***********

Solosis uses `pip-tools <https://github.com/jazzband/pip-tools>`_ to manage and lock dependencies.  
Dependencies are declared in ``pyproject.toml`` and compiled into pinned requirements files to ensure reproducible environments.

To update locked dependencies:

::

    pip-compile --output-file=envs/requirements.txt
    pip-compile --extra=dev --output-file=envs/dev-requirements.txt
    pip-compile --extra=dev --output-file=envs/doc-requirements.txt

Synchronise your environment:

::

    pip-sync envs/requirements.txt
    pip-sync envs/dev-requirements.txt
    pip-sync envs/doc-requirements.txt

This will install exactly the packages and versions listed in the specified files, removing any packages not included.

To upgrade dependencies, add ``--upgrade``:

::

    pip-compile --upgrade --output-file=envs/requirements.txt

pytest
******

To run tests using `pytest`_:

::

    python -m pytest -q tests/test_cli.py
