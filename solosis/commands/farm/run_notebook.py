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

from .. import helpers

# Script directory in the solosis package
script_dir = os.path.dirname(os.path.abspath(__file__))
codebase = os.path.join(script_dir, "../../../bin/")


def _assign_job_name(job_name, ctx):
    """
    Assign a job name to the job.
    """
    if job_name == "default":
        job_name = f"{ctx.obj['execution_id']}"
    else:
        job_name = f"{job_name}_{ctx.obj['execution_id']}"
    return job_name


@click.command("run_ipynb")
@helpers.job_resources
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
@click.pass_context
def cmd(ctx, notebook, job_name, **kwargs):
    """
    Run a jupyter notebook on the farm.
    """
    log_command(ctx)
    job_name = _assign_job_name(job_name, ctx)
    # To do: Install jupyter in base solosis conda env
    command_to_exec = f"source ~/.bashrc && conda activate /software/cellgen/team298/shared/envs/hl-conda/hl_minimal_v1.0.0 && jupyter nbconvert --to notebook --execute {notebook}"
    echo_message(f"Job name :{job_name} submitted to queue: {kwargs.get('queue')}")
    _single_command_bsub(command_to_exec, job_name=job_name, **kwargs)
