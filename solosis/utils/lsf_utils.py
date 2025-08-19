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


def lsf_job(mem=64000, cpu=2, time="12:00", queue="normal", gpu=False):
    """
    Decorator to add LSF job options to a click command.

    Usage:
        @click.command()
        @lsf_job(mem=20000, cpu=4, gpu=True)
        def cmd(mem, cpu, time, queue, gpu):
            pass
    """

    def decorator(function):
        function = click.option(
            "--mem",
            default=mem,
            type=int,
            show_default=True,
            help="Memory limit (in MB)",
        )(function)
        function = click.option(
            "--cpu",
            default=cpu,
            type=int,
            show_default=True,
            help="Number of CPU cores",
        )(function)
        function = click.option(
            "--queue",
            default=queue,
            type=str,
            show_default=True,
            help="Queue to which the job should be submitted",
        )(function)
        function = click.option(
            "--gpu",
            is_flag=True,
            default=gpu,
            show_default=True,
            help="Request a GPU with default settings",
        )(function)
        function = click.option(
            "--time", default=time, type=str, help="Number of GPUs to request"
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
    gpu: bool = False,
):
    """
    Submit an LSF job array where each job runs a command from a file.

    Args:
        command_file (str): Path to the file containing one command per line.
        job_name (str, optional): Name for the job array. Defaults to "job_array".
        cpu (int, optional): Number of CPU cores per job. Defaults to 16.
        mem (int, optional): Memory limit in MB per job. Defaults to 64000.
        queue (str, optional): LSF queue name. Defaults to "normal".
        group (str, optional): User group for LSF submission. Defaults to value in LSB_DEFAULT_USERGROUP.
        gpu (bool, optional): Whether to request GPU resources. Defaults to False.
    """
    if group is None:
        group = os.environ.get("LSB_DEFAULT_USERGROUP")

    if not group or not group.startswith("team"):
        logger.error(f"Group '{group}' is invalid. Exiting.")
        raise click.Abort()

    if not os.path.isfile(command_file) or os.stat(command_file).st_size == 0:
        logger.error(
            f"Command file '{command_file}' does not exist or is empty. Exiting."
        )
        raise click.Abort()

    with open(command_file, "r") as f:
        num_commands = sum(1 for _ in f)

    if not execution_uid:
        raise ValueError("The execution_uid is empty or None. It must be a valid UUID.")

    log_dir = Path(os.getenv("SOLOSIS_LOG_DIR")) / execution_uid
    os.makedirs(log_dir, exist_ok=True)

    # Override queue and set GPU options if requested
    gpu_options = ""
    if gpu:
        queue = "gpu-normal"
        gpumem = 6000
        gpunum = 1
        gpumodel = "NVIDIAA100_SXM4_80GB"
        gpu_options = f'#BSUB -gpu "mode=shared:j_exclusive=no:gmem={gpumem}:num={gpunum}:gmodel={gpumodel}"'
        cpu = 4
        mem = 16000

    # Construct the LSF job submission script
    lsf_script = f"""#!/bin/bash
#BSUB -J "{job_name}[1-{num_commands}]"
#BSUB -o "{log_dir}/lsf_{job_name}_%J_%I.out"
#BSUB -e "{log_dir}/lsf_{job_name}_%J_%I.err"
#BSUB -n {cpu}
#BSUB -M {mem}
#BSUB -R "span[hosts=1] select[mem>{mem}] rusage[mem={mem}]"
#BSUB -G "{group}"
#BSUB -q "{queue}"
#BSUB -Ep /software/cellgen/cellgeni/etc/notify-slack.sh
{gpu_options}

COMMAND=$(sed -n "${{LSB_JOBINDEX}}p" "{command_file}")
echo "Executing command: $COMMAND"
eval "$COMMAND"
"""

    # Submit the job array
    logger.debug(f"LSF Script: {lsf_script}")
    try:
        process = subprocess.run(
            ["bsub"], input=lsf_script, text=True, capture_output=True, check=True
        )
        logger.info(f"Job submitted successfully: {process.stdout.strip()}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Error submitting job: {e.stderr}")


def submit_lsf_job(
    command: str,
    job_name: str = "single_job",
    cpu: int = 16,
    mem: int = 64000,
    queue: str = "normal",
    group: str = None,
    gpu: bool = False,
    execution_uid: str = None,
):
    """
    Submit a single LSF job based on a command.

    Args:
        command (str): The shell command to run.
        job_name (str, optional): Name for the job. Defaults to "single_job".
        cpu (int, optional): Number of CPU cores. Defaults to 16.
        mem (int, optional): Memory limit in MB. Defaults to 64000.
        queue (str, optional): LSF queue name. Defaults to "normal".
        group (str, optional): User group for LSF submission. Defaults to value in LSB_DEFAULT_USERGROUP.
        gpu (bool, optional): Whether to request GPU resources. Defaults to False.
        execution_uid (str, optional): Unique identifier for this execution (used for log dir). Required.
    """
    if group is None:
        group = os.environ.get("LSB_DEFAULT_USERGROUP")

    if not group or not group.startswith("team"):
        logger.error(f"Group '{group}' is invalid. Exiting.")
        raise ValueError(f"Invalid group: {group}")

    if not execution_uid:
        raise ValueError("execution_uid is required and cannot be empty")

    log_dir = Path(os.getenv("SOLOSIS_LOG_DIR", "/tmp")) / execution_uid
    os.makedirs(log_dir, exist_ok=True)

    # Override queue and set GPU options if requested
    gpu_options = ""
    if gpu:
        queue = "gpu-normal"
        gpumem = 6000
        gpunum = 1
        gpumodel = "NVIDIAA100_SXM4_80GB"
        gpu_options = f'#BSUB -gpu "mode=shared:j_exclusive=no:gmem={gpumem}:num={gpunum}:gmodel={gpumodel}"'
        cpu = 4
        mem = 16000

    # Construct the LSF job submission script
    lsf_script = f"""#!/bin/bash
#BSUB -J "{job_name}"
#BSUB -o "{log_dir}/lsf_{job_name}_%J.out"
#BSUB -e "{log_dir}/lsf_{job_name}_%J.err"
#BSUB -n {cpu}
#BSUB -M {mem}
#BSUB -R "span[hosts=1] select[mem>{mem}] rusage[mem={mem}]"
#BSUB -G "{group}"
#BSUB -q "{queue}"
#BSUB -Ep /software/cellgen/cellgeni/etc/notify-slack.sh
{gpu_options}

echo "Executing command: {command}"
eval "{command}"
"""

    # Submit the job
    logger.debug(f"LSF Script: {lsf_script}")
    try:
        process = subprocess.run(
            ["bsub"], input=lsf_script, text=True, capture_output=True, check=True
        )
        logger.info(f"Job submitted successfully: {process.stdout.strip()}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Error submitting job: {e.stderr}")
        raise
