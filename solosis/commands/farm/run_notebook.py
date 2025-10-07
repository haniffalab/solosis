import logging
import os
import tempfile

import click

from solosis.utils.logging_utils import debug, log
from solosis.utils.lsf_utils import lsf_job, submit_lsf_job_array
from solosis.utils.state import execution_uid, logger


@lsf_job(mem=64000, cpu=1, queue="normal", time="12:00")
@click.command("run-ipynb")
@click.option(
    "-n", "--notebook", required=True, type=str, help="Path to the notebook to run"
)
@click.option(
    "-j",
    "--job_name",
    required=False,
    type=str,
    help="Name of the job. If not provided, the execution UID will be used",
    default="default",
)
@debug
@log
def cmd(notebook, job_name, mem, cpu, queue, gpu, gpumem, time, debug, **kwargs):
    """Submit a Jupyter notebook to run via LSF"""
    if debug:
        logger.setLevel(logging.DEBUG)

    ctx = click.get_current_context()
    logger.debug(
        f"Starting command: {click.style(ctx.command.name, bold=True, underline=True)}"
    )
    job_name = execution_uid if job_name == "default" else f"{job_name}_{execution_uid}"
    logger.debug(f"Job name: {job_name}")

    # @TODO: Ensure all kwargs are strings for environment variables
    env_vars = {str(k): str(v) for k, v in kwargs.items()}

    # Construct command
    command_str = (
        f"source ~/.bashrc && "
        f"conda activate /software/cellgen/team298/shared/envs/hl-conda/hl_minimal_v1.0.0 && "
        f"jupyter nbconvert --to notebook --execute {notebook}"
    )

    # Submit the job
    with tempfile.NamedTemporaryFile(
        delete=False, mode="w", suffix=".txt", dir=os.environ["TEAM_TMP_DIR"]
    ) as tmpfile:
        logger.debug(f"Temporary command file created: {tmpfile.name}")
        os.chmod(tmpfile.name, 0o660)
        tmpfile.write(command_str + "\n")

    submit_lsf_job_array(
        command_file=tmpfile.name,
        job_name=job_name,
        cpu=cpu,
        mem=mem,
        queue=queue,
        gpu=gpu,
        gpumem=gpumem,
    )


if __name__ == "__main__":
    cmd()
