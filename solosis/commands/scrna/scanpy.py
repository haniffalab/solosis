import logging
import os

import click

from solosis.utils.logging_utils import debug, log
from solosis.utils.lsf_utils import lsf_job, submit_lsf_job
from solosis.utils.state import execution_uid, logger


@lsf_job(mem=64000, cpu=4, queue="normal", time="12:00")
@click.command("scanpy")
@click.option("--samplefile", required=True, help="Sample file text file")
@click.option(
    "--sample_basedir",
    required=False,
    default="/lustre/scratch124/cellgen/haniffa/sample_data/",
    help="Sample database folder",
)
@click.option(
    "--job_name",
    required=False,
    type=str,
    default="scanpy",
    help="Optional name for the LSF job. Defaults to scanpy_<uid>.",
)
@debug
@log
def cmd(
    samplefile, sample_basedir, job_name, mem, cpu, queue, gpu, time, debug, **kwargs
):
    """
    Submit Scanpy workflow for scRNA-seq data as a job on the compute farm.

    Input samplefile should have 3 mandatory columns:
    1st column: sanger_id, 2nd column: sample_name, 3rd column: irods path
    """
    if debug:
        logger.setLevel(logging.DEBUG)

    ctx = click.get_current_context()
    logger.debug(
        f"Starting command: {click.style(ctx.command.name, bold=True, underline=True)}"
    )

    # Path to the shell script
    shell_script = os.path.abspath(
        os.path.join(
            os.getenv("SCRIPT_BIN"),
            "scrna/scanpy/submit.sh",
        )
    )

    if not os.path.exists(shell_script):
        logger.error(f"Shell script not found: {shell_script}")
        return

    # Compose job name
    job_name = execution_uid if job_name == "scanpy" else f"{job_name}_{execution_uid}"
    logger.info(f"Submitting Scanpy job: {job_name} to queue {queue}")

    # Pass extra kwargs as environment variables
    env_vars = {str(k): str(v) for k, v in kwargs.items()}

    # Submit the job via LSF
    submit_lsf_job(
        command=f"{shell_script} {sample_basedir} {samplefile}",
        job_name=job_name,
        mem=mem,
        cpu=cpu,
        queue=queue,
        gpu=gpu,
        execution_uid=execution_uid,
        env=env_vars,
    )


if __name__ == "__main__":
    cmd()
