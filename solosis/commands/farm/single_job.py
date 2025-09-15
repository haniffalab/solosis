import logging
import os
import tempfile

import click

from solosis.utils.logging_utils import debug, log
from solosis.utils.lsf_utils import lsf_job, submit_lsf_job_array
from solosis.utils.state import execution_uid, logger


@lsf_job(mem=64000, cpu=1, queue="normal", time="12:00")
@click.command("single-job")
@click.argument("command_to_exec", nargs=-1, type=str)
@click.option(
    "-j",
    "--job_name",
    required=False,
    type=str,
    help="Optional name of the job. If not provided, the execution UID is used.",
    default="default",
)
@debug
@log
def cmd(command_to_exec, job_name, mem, cpu, queue, gpu, time, debug, **kwargs):
    """Submit a single comamnd via LSF"""
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

    if not command_to_exec:
        logger.error("No command to execute")
        return

    # Convert tuple of strings to a single string
    command_str = " ".join(command_to_exec)

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
    )


if __name__ == "__main__":
    cmd()
