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

        # Check for the specific error in stderr
        if (
            "CAT_INVALID_AUTHENTICATION" in result.stderr
            or "-827000 CAT_INVALID_USER" in result.stderr
        ):
            secho(
                "run `iinit` before re-running this solosis command.",
                "error",
            )
            sys.exit(1)  # Exit with error status 1

        # If no error, command executed successfully
        secho("Command executed successfully.", "success")

    except FileNotFoundError:
        secho(
            "iRODS not loaded. please run `module load cellgen/irods` before re-running this solosis command.",
            "error",
        )
        sys.exit(1)
