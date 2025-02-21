import csv
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


def irods_auth():

    # Load the iRODS module
    try:
        secho("Checking iRODS status...", "info")
        module_result = subprocess.run(
            ["iget"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
        )
    except FileNotFoundError:
        secho(
            "'iget' command not found (FileNotFoundError)",
            "error",
        )
        sys.exit(1)
        load_irods_module()
        return

    # Check stderr for "Command 'iget' not found, did you mean:"
    if "Command 'iget' not found, did you mean:" in result.stderr:
        secho("'iget' command not found. Attempting to load iRODS module...", "error")
        sys.exit(1)
        load_irods_module()
        return

    # Step 4: Check authentication error
    if (
        "CAT_INVALID_AUTHENTICATION" in result.stderr
        or "-827000 CAT_INVALID_USER" in result.stderr
    ):
        secho(
            "Authentication failed. Run `iinit` before re-running this command.",
            "error",
        )
        sys.exit(1)
        sys.exit(1)

    sys.exit(1)
    """Run a command and handle specific output conditions."""
    command = [
        "iget",
        "/seq/illumina/runs/48/48297/cellranger/cellranger720_count_48297_58_rBCN14591738_GRCh38-2020-A/web_summary.html",
    ]

    try:
        # Run the command and capture stdout and stderr
        result = subprocess.run(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )

        # If the command is successful, print a success message
        secho("Command executed successfully.", "success")

    except FileNotFoundError as e:
        # Check if the error is because 'iget' is not found
        if "Command 'iget' not found" in str(e):
            secho("'iget' command not found. Loading iRODS module...", "info")
            # Try loading the iRODS module
            try:
                subprocess.run(["module", "load", "cellgen/irods"], check=True)
                secho("Module 'cellgen/irods' loaded successfully.", "success")
                # Retry the original command after loading the module
                result = subprocess.run(
                    command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
                )
                secho("Command executed successfully.", "success")
            except subprocess.CalledProcessError:
                secho(
                    "Failed to load the iRODS module. Please ensure that the module is available.",
                    "error",
                )
                sys.exit(1)

        else:
            # Handle other FileNotFoundError cases
            secho(
                "iRODS not loaded. please run `module load cellgen/irods` before re-running this solosis command.",
                "error",
            )
            sys.exit(1)

    # Handle specific iRODS authentication errors
    if (
        "CAT_INVALID_AUTHENTICATION" in result.stderr
        or "-827000 CAT_INVALID_USER" in result.stderr
    ):
        secho(
            "run `iinit` before re-running this solosis command.",
            "error",
        )
        sys.exit(1)


def load_irods_module():
    """Load the iRODS module and exit if unsuccessful."""
    try:
        module_result = subprocess.run(
            ["module", "load", "cellgen/irods"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
        )
        print(module_result.stdout)
        print(module_result.stderr, file=sys.stderr)

    except subprocess.CalledProcessError:
        secho(
            "Failed to load the iRODS module. Ensure the module is available.", "error"
        )
        sys.exit(1)

    secho("Successfully loaded the iRODS module. Please retry your command.", "success")
