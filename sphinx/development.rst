.. _development:

Development
===========

If you are developing or want to contribute to Solosis, please read this page.

You can clone the repo to your preferred development location

::

    git clone git@github.com:haniffalab/solosis.git
    cd solosis

Create and activate the virtual environment

::

    python -m venv .venv
    source .venv/bin/activate

Install dev dependencies and install pre-commit hooks

::

    python -m pip install -r envs/dev/requirements.txt
    pre-commit install
    
For Github Actions to pass, will need to ensure ``black`` formatting and ``isort`` are implemented.
You can manually check ``black`` formatting and ``isort``

::

    black path/to/file.py

    isort path/to/file.py

Python testing
--------------

**Testing of python scripts uses `pytest`_.**

Set the :code:`PYTHONPATH` environment variable to the :code:`bin` directory where the scripts are stored, and then run the following command:

::

    python -m pytest -q tests/test_cli.py

.. _pytest: https://docs.pytest.org/en/7.1.x/

.. **Environment Variables**

.. The following environment variables are required to be set for the Solosis module to work correctly.

.. .. code-block:: shell
..    :caption: Input

..    export TEAM_DATA_DIR="/lustre/scratch126/cellgen/team298/data"
..    export TEAM_LOGS_DIR="/lustre/scratch126/cellgen/team298/logs"
..    export LSB_DEFAULT_USERGROUP="team298"

