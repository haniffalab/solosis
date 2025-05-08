import os
import subprocess
import click
from solosis.utils.farm import (
    _single_command_bsub,
    bash_submit,
    echo_lsf_submission_message,
    echo_message,
    log_command,

)
from solosis.utils.input_utils import collect_samples
from solosis.utils.logging_utils import debug, log
from solosis.utils.lsf_utils import lsf_job, submit_lsf_job_array
from solosis.utils.state import execution_uid, logger


# Script directory in the solosis package
codebase = os.getenv("SCRIPT_BIN")


def _assign_job_name(job_name, execution_uid):
    """
    Assign a job name to the job.
    """
    if job_name == "default":
        job_name = execution_uid
    else:
        job_name = f"{job_name}_{execution_uid}"
    return job_name


@lsf_job(mem=64000, cpu=1, queue="normal", time="12:00")
@click.command("run_ipynb")
#@helpers.job_resources
@click.option(
    "-n", "--notebook", required=True, type=str, help="Path to the notebook to run"
)
@click.option(
    "-j",
    "--job_name",
    required=False,
    type=str,
    help="Name of the job",
    default="default",
)  # random val to be implemented (from import random)
@debug
@log
#@click.pass_context
def cmd(notebook, job_name, **kwargs):
    """
    Run a jupyter notebook on the farm.
    """
    ctx = click.get_current_context()
    job_name = _assign_job_name(job_name, execution_uid)
    # To do: Install jupyter in base solosis conda env
    command_to_exec = f"source ~/.bashrc && conda activate /software/cellgen/team298/shared/envs/hl-conda/hl_minimal_v1.0.0 && jupyter nbconvert --to notebook --execute {notebook}"
    logger.info(f"Job name :{job_name} submitted to queue: {kwargs.get('queue')}")
    _single_command_bsub(command_to_exec, job_name=job_name, **kwargs)
