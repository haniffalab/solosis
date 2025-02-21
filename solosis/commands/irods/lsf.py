import os
import subprocess
import sys
import tempfile

import click
import pandas as pd

from solosis.utils.env_utils import irods_auth
from solosis.utils.logging_utils import secho
from solosis.utils.lsf_utils import lsf_options, submit_lsf_job_array


@lsf_options
@click.command("lsf")
@click.option("--sample", type=str, help="Sample ID (string).")
@click.option(
    "--samplefile",
    type=click.Path(exists=True),
    help="Path to a CSV or TSV file containing sample IDs.",
)
def cmd(sample, samplefile, mem, cores, time, queue):
    """
    Submits an LSF job array with dummy commands.
    """
    ctx = click.get_current_context()
    secho(
        f"Starting Process: {click.style(ctx.command.name, bold=True, underline=True)}",
        "info",
    )

    # Define the directory where you want to create the temp file
    temp_dir = os.path.join(os.environ.get("TEAM_DATA_DIR"), "tmp", "lsf")
    os.makedirs(temp_dir, exist_ok=True)

    # Create a temporary file to hold the dummy commands
    with tempfile.NamedTemporaryFile(
        delete=False, mode="w", suffix=".txt", dir=temp_dir
    ) as tmpfile:
        tmpfile.write("echo 'Job 1 running'\n")
        tmpfile.write("echo 'Job 2 running'\n")
        tmpfile.write("echo 'Job 3 running'\n")
        tmpfile_path = tmpfile.name

    secho(f"Temporary command file created: {tmpfile_path}")

    # Submit the job using lsf_job_array
    submit_lsf_job_array(
        command_file=tmpfile_path,
        job_name="dummy_job_array",  # Example job name
        cpu=cores,
        mem=mem,
        queue=queue,
    )
    # Clean up the temporary file after submission
    os.chmod(tmpfile_path, 0o660)
    secho("Temporary file removed after submission.")


if __name__ == "__main__":
    cmd()
