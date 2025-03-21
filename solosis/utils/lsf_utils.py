import functools
import os
import subprocess
from pathlib import Path

import click

from solosis.utils.state import execution_uid, logger

VALID_GPUS = {
    "NVIDIAA100_SXM4_80GB",
    "TeslaV100_SXM2_32GB",
    "TeslaV100_SXM2_16GB",
    "TeslaV100_SXM2_32GB",
    "NVIDIAH10080GBHBM3",
}


def lsf_options_sm(function):
    function = click.option(
        "--mem", default=4000, type=int, help="Memory limit (in MB)"
    )(function)
    function = click.option("--cpu", default=2, type=int, help="Number of CPU cores")(
        function
    )
    function = click.option(
        "--queue", default="small", help="Queue to which the job should be submitted"
    )(function)
    return function


def lsf_options_std(function):
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


def lsf_job(mem=64000, cpu=2, time="12:00", queue="normal", gpu=None):
    """
    Decorator to add LSF job options to a click command.
    Usage:
        @click.command()
        @lsf_job(mem=20000, cpu=4, gpu="NVIDIAA100_SXM4_80GB")
        def cmd(mem, cpu, time, queue, gpu):
            pass
    """

    def decorator(function):
        function = click.option(
            "--mem", default=mem, type=str, help="Memory limit (in MB)"
        )(function)
        function = click.option(
            "--cpu", default=cpu, type=str, help="Number of CPU cores"
        )(function)
        function = click.option(
            "--queue", default=queue, help="Queue to which the job should be submitted"
        )(function)
        function = click.option(
            "--gpu", default=gpu, type=str, help="Number of GPUs to request"
        )(function)
        return function

    return decorator


def submit_lsf_job_array(
    command_file: str,
    job_name: str = "job_array",
    cpu: int = 16,
    mem: int = 64000,
    queue: str = "normal",
    group: str = None,
    gpu: str = None,
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
        logger.error(f"Group '{group}' does not start with 'team'. Exiting.")
        raise click.Abort()

    if not os.path.isfile(command_file) or os.stat(command_file).st_size == 0:
        logger.error(
            f"Command file '{command_file}' does not exist or is empty. Exiting."
        )
        raise click.Abort()

    with open(command_file, "r") as f:
        num_commands = sum(1 for _ in f)

    if not execution_uid:
        raise ValueError("execution_uid is empty or None. It must be a valid UUID.")

    log_dir = Path(os.getenv("SOLOSIS_LOG_DIR")) / execution_uid
    os.makedirs(log_dir, exist_ok=True)

    # Validate GPU options
    if gpu:
        if gpu not in VALID_GPUS:
            raise ValueError(f"Invalid GPU type '{gpu}'. Must be one of: {VALID_GPUS}")

        queue = "gpu-normal"
        gpumem = 6000
        gpunum = 1

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
"""
    # Validate and add GPU options if specified
    if gpu:
        lsf_script += f"""#BSUB -gpu "mode=shared:j_exclusive=no:gmem={gpumem}:num={gpunum}:gmodel={gpu}"\n"""

    # Extract and run the command
    lsf_script += f"""
COMMAND=$(sed -n "${{LSB_JOBINDEX}}p" "{command_file}")
echo "Executing command: $COMMAND"
eval "$COMMAND"
"""

    # Print the GPU value before submission
    logger.info(f"Script: {lsf_script}")
    click.Abort()

    # Submit the job array
    try:
        process = subprocess.run(
            ["bsub"], input=lsf_script, text=True, capture_output=True, check=True
        )
        logger.info(f"Job submitted successfully: {process.stdout.strip()}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Error submitting job: {e.stderr}")
