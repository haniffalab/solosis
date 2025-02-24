import os
import subprocess
import sys
from pathlib import Path

import click

from solosis.utils.logging_utils import secho
from solosis.utils.state import execution_uid


def lsf_options(function):
    function = click.option(
        "--mem", default=64000, type=int, help="Memory limit (in MB)"
    )(function)
    function = click.option("--cpu", default=16, type=int, help="Number of CPU cores")(
        function
    )
    function = click.option(
        "--queue", default="normal", help="Queue to which the job should be submitted"
    )(function)
    return function


def submit_lsf_job_array(
    command_file: str,
    job_name: str = "job_array",
    cpu: int = 16,
    mem: int = 64000,
    queue: str = "normal",
    group: str = None,
):
    """
    Submit an LSF job array where each job runs a command from a file.

    Args:
        command_file (str): Path to the file containing one command per line.
        job_name (str, optional): Name for the job array. Defaults to "command_array".
        cpu (int, optional): Number of CPU cores per job. Defaults to 16.
        mem (int, optional): Memory limit in MB per job. Defaults to 64000.
        queue (str, optional): LSF queue name. Defaults to "normal".
        group (str, optional): User group for LSF submission. Defaults to "team298".
    """

    if group is None:
        group = os.environ.get("LSB_DEFAULT_USERGROUP")

    if not group.startswith("team"):
        secho(
            f"Error: Group '{group}' does not start with 'team'. Exiting.",
            fg="red",
            err=True,
        )
        sys.exit(1)

    if not os.path.isfile(command_file) or os.stat(command_file).st_size == 0:
        secho(
            f"Error: Command file '{command_file}' does not exist or is empty.",
            fg="red",
            err=True,
        )
        return

    with open(command_file, "r") as f:
        num_commands = sum(1 for _ in f)

    if not execution_uid:
        raise ValueError("execution_uid is empty or None. It must be a valid UUID.")

    log_dir = Path(os.getenv("SOLOSIS_LOG_DIR")) / execution_uid
    os.makedirs(log_dir, exist_ok=True)

    # Construct the LSF job submission script
    lsf_script = f"""#!/bin/bash
#BSUB -J "{job_name}[1-{num_commands}]"
#BSUB -o "{log_dir}/lsf_{job_name}_%J_%I.out"
#BSUB -e "{log_dir}/lsf_{job_name}_%J_%I.err"
#BSUB -n {cpu}
#BSUB -M {mem}
#BSUB -R "span[hosts=1] select[mem>{mem}] rusage[mem={mem}]"
#BSUB -G "{group}"
#BSUB -q {queue}

# Extract the command for this job index
COMMAND=$(sed -n "${{LSB_JOBINDEX}}p" "{command_file}")

# Debug: output the command being executed
echo "Executing command: $COMMAND"

# Run the command
eval "$COMMAND"
"""

    # Submit the job array
    try:
        process = subprocess.run(
            ["bsub"], input=lsf_script, text=True, capture_output=True, check=True
        )
        secho(f"Job submitted successfully: {process.stdout.strip()}", "success")
    except subprocess.CalledProcessError as e:
        secho(f"Error submitting job: {e.stderr}", "error")
