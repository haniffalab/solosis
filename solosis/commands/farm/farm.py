import os
import subprocess
import click
from .. import helpers
from solosis.utils import echo_lsf_submission_message, echo_message, log_command

# Script directory in the solosis package
script_dir = os.path.dirname(os.path.abspath(__file__))  


## Functions supporting farm submission
def bash_submit(job_runner: str, **kwargs) -> None:
    """
    Runs a command. Command can be a bash command (du -hs ) or a script (test.sh)
    While running exports all kwargs as environment variables
    This can be reused to run any bash script in all the subcommands
    If the command needs to be submitted to farm use single_command or array_command
    """
    # env variables are set to
    for k, v in kwargs.items():
        kwargs[str(k)] = str(v)
    # Capture result
    result = subprocess.run(
        [job_runner], capture_output=True, text=True, env={**os.environ, **kwargs}
    )

    click.echo(result.stdout)
    click.echo(result.stderr)


def _single_command_bsub(command_to_exec, job_name, queue, time, cores, mem, **kwargs):
    """
    Run a single command on the farm.
    """
    job_runner = os.path.abspath(
        os.path.join(script_dir, "../../../bin/farm/single_job.sh")
        )
    if len(command_to_exec) == 0:
        echo_message("No command to execute", type="error")
        return
    
    command_to_exec = " ".join(command_to_exec)
    bash_submit(
        job_runner,
        command_to_exec=command_to_exec,
        job_name=job_name,
        queue=queue,
        time=time,
        cores=cores,
        mem=mem,
    )




@click.command("command")
@helpers.job_resources
@click.argument("command_to_exec", nargs=-1, type=str)
@click.option("-j", "--job_name", required=False, type=str, help="Name of the job", default="default")  # random val to be implemented (from import random)
@click.pass_context
def single_cmd(ctx, command_to_exec, job_name, **kwargs):
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
    help="Name of the job",
)  # random val to be implemented (from import random)


def run_ipynb(notebook, job_name, **kwargs):
    """
    Run a jupyter notebook on the farm.
    """
    job_runner = os.path.join(codebase, "single_job.sh")
    # To do: Install jupyter in base solosis conda env
    command_to_exec = f"source ~/.bashrc && conda activate /software/cellgen/team298/shared/envs/hl-conda/hl_minimal_v1.0.0 && jupyter nbconvert --to notebook --execute {notebook}"
    bash_submit(
        job_runner, command_to_exec=command_to_exec, job_name="notebook", **kwargs
    )


if __name__ == "__main__":
    cmd = os.path.join(codebase, "test.sh")
    bash_submit(cmd, command_to_exec='echo "Hello, World!"')
