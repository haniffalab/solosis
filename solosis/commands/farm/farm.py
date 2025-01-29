import os
import subprocess
import click
from .. import helpers


# Script directory in the solosis package
script_dir = os.path.dirname(os.path.abspath(__file__))  


## Functions supporting farm submission
def bash_submit(command: str, **kwargs) -> None:
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
        [command], capture_output=True, text=True, env={**os.environ, **kwargs}
    )
    click.echo(result.stdout)
    click.echo(result.stderr)


def single_command(command_to_exec, job_name, queue, time, cores, mem, **kwargs):
    """
    Run a single command on the farm.
    """
    job_runner = os.path.abspath(
        os.path.join(script_dir, "../../../bin/alignment/cellranger-count/submit.sh")
        )
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
@helpers.farm
@click.argument("command_to_exec", nargs=-1, type=str)
@click.option("-j", "--job_name", required=False, type=str, help="Name of the job", default="random_val")  # random val to be implemented (from import random)
def single_cmd(command_to_exec, job_name, **kwargs):
    """
    Run a single command on the farm.
    """
    queue = kwargs.get("queue")
    time = kwargs.get("time")
    cores = kwargs.get("cores")
    mem = kwargs.get("mem")
    single_command(command_to_exec, job_name=job_name, **kwargs)


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
    default="random_val",
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
    )  # , queue=queue, time=time, cores=cores, mem=mem)


if __name__ == "__main__":
    cmd = os.path.join(codebase, "test.sh")
    bash_submit(cmd, command_to_exec='echo "Hello, World!"')
