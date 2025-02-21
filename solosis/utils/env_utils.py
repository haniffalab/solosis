import csv
import getpass
import os
import re
import subprocess
import sys
from datetime import datetime

import click

from solosis.utils.logging_utils import secho


def validate(required_vars):
    """Validates that all required environment variables are set."""
    for var in required_vars:
        if not os.getenv(var):
            secho(
                f"Environment variable '{var}' is not set. Please export it before running Solosis.",
                "error",
            )
            raise click.Abort()


def irods_auth(timeout=5):
    """Validate irods authentication."""
    try:
        secho("Checking iRODS authentication status...", "info")
        result = subprocess.run(
            ["iget", "dummy"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
            timeout=timeout,
        )

        # Capture errors from stderr even if the command "succeeded" but returned errors
        if result.returncode != 0:
            # Check if the error indicates that the user is authenticated
            if "USER_INPUT_PATH_ERR" in result.stderr:
                secho("iRODS authenticated.", "success")
                return True

            secho(f"iget command failed with return code {result.returncode}", "error")
            secho(f"Standard Output:\n{result.stdout}", "info")
            secho(f"Standard Error:\n{result.stderr}", "error")

    except Exception as e:
        # Assuming error is a timeout, indicating user in not authenticated.
        password = getpass.getpass("Enter iRODS Password: ")
        subprocess.run(["stty", "sane"])  # Needed to reset terminal state
        process = subprocess.Popen(
            ["iinit"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        process.communicate(input=password + "\n")
        if process.returncode == 0:
            secho(f"iRODS authenticated...", "success")
            return True
        else:
            secho(f"iRODS initialization failed", "error")

    return False
