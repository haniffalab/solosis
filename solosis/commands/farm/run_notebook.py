import os
import subprocess
import click
from .. import helpers
from solosis.utils import echo_lsf_submission_message, echo_message, log_command, bash_submit, _single_command_bsub

# Script directory in the solosis package
script_dir = os.path.dirname(os.path.abspath(__file__))  
codebase = os.path.join(script_dir, "..", "..", "codebase")



@click.command("run_ipynb")
@helpers.farm
@click.option(
    "-n", "--notebook", required=True, type=str, help="Path to the notebook to run"
)
@click.option(
    "-j",
    "--job_name",
    required=False,
    type=str,
    help="Name of the job"
)  
@click.pass_context

def run_ipynb(ctx, notebook, job_name, **kwargs):
    """
    Run a jupyter notebook on the farm.
    """
    job_runner = os.path.join(codebase, "single_job.sh")
    # To do: Install jupyter in base solosis conda env
    command_to_exec = f"source ~/.bashrc && conda activate /software/cellgen/team298/shared/envs/hl-conda/hl_minimal_v1.0.0 && jupyter nbconvert --to notebook --execute {notebook}"
    bash_submit(
        job_runner, command_to_exec=command_to_exec, job_name="notebook", **kwargs
    )


