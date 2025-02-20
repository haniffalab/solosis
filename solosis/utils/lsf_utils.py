import os
import subprocess

import click

from solosis.utils.logging_utils import secho


def lsf_options(function):
    function = click.option("--mem", default=50000, type=int, help="mem in MB")(
        function
    )
    function = click.option("--cores", default=4, type=int, help="# of cores")(function)
    function = click.option("--time", default="12:00:00", help="time for running")(
        function
    )
    function = click.option("--queue", default="normal", help="queue name")(function)
    return function


def submit_lsf_job_array(
    command_file: str,
    job_name: str = "command_array",
    cpu: int = 16,
    mem: int = 64000,
    queue: str = "normal",
    group: str = "team298",
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

    if not os.path.isfile(command_file) or os.stat(command_file).st_size == 0:
        secho(
            f"Error: Command file '{command_file}' does not exist or is empty.",
            fg="red",
            err=True,
        )
        return

    # Count the number of commands
    with open(command_file, "r") as f:
        num_commands = sum(1 for _ in f)

    log_dir = "command_logs"
    os.makedirs(log_dir, exist_ok=True)

    # Construct the LSF job submission script
    lsf_script = f"""#!/bin/bash
#BSUB -J "{job_name}[1-{num_commands}]"
#BSUB -o "{log_dir}/{job_name}_%J_%I.out"
#BSUB -e "{log_dir}/{job_name}_%J_%I.err"
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
        secho(f"Job submitted successfully: {process.stdout.strip()}", fg="green")
    except subprocess.CalledProcessError as e:
        secho(f"Error submitting job: {e.stderr}", fg="red", err=True)
