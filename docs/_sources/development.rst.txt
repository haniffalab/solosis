.. _development:

.. _pytest: https://docs.pytest.org/en/7.1.x/

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

Testing of python scripts uses pytest_. Set the :code:`PYTHONPATH` environment variable
to the :code:`bin` directory where the scripts are stored, and then run the following command:

::

    python -m pytest -q tests/test_cli.py



