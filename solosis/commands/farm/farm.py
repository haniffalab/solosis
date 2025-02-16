import os
import subprocess
import click
from .. import helpers
from solosis.utils import echo_lsf_submission_message, echo_message, log_command, bash_submit, _single_command_bsub

# Script directory in the solosis package
script_dir = os.path.dirname(os.path.abspath(__file__))  


@click.command("command")
@helpers.job_resources
@click.argument("command_to_exec", nargs=-1, type=str)
@click.option("-j", "--job_name", required=False, type=str, help="Name of the job", default="default")  # random val to be implemented (from import random)
@click.pass_context
def cmd(ctx, command_to_exec, job_name, **kwargs):
    """
    Run a single command on the farm.
    """
    queue = kwargs.get("queue")
    time = kwargs.get("time")
    cores = kwargs.get("cores")
    mem = kwargs.get("mem")
    log_command(ctx)
    if job_name == "default":
        job_name = f"{ctx.command_path}_{ctx.obj['execution_id']}"
    else:
        job_name = f"{job_name}_{ctx.obj['execution_id']}"
    echo_lsf_submission_message(f"Job name :{job_name} submitted to queue: {queue}")
    _single_command_bsub(command_to_exec, job_name=job_name, **kwargs)
    



if __name__ == "__main__":
    cmd = os.path.join(codebase, "test.sh")
    bash_submit(cmd, command_to_exec='echo "Hello, World!"')
