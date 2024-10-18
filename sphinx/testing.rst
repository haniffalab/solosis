.. _testing:

Testing
=======

Python testing
--------------

**Development**

For Github Actions to pass, will need to ensure ``black`` formatting and ``isort`` are implemented.

Create virtual environment

::

    python -m venv .venv
    source .venv/bin/activate

Install dev dependencies and install pre-commit hooks, this is automated.

::

    python -m pip install -r envs/dev/requirements.txt
    pre-commit install
    

Manually checking ``black`` formatting and ``isort``.

::

    black path/to/file.py

    isort path/to/file.py

**Testing of python scripts uses `pytest`_.**

Set the :code:`PYTHONPATH` environment variable to the :code:`bin` directory where the scripts are stored, and then run the following command:

::

    python -m pytest -q tests/test_class.py

.. _pytest: https://docs.pytest.org/en/7.1.x/




