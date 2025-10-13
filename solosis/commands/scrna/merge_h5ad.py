import logging
import os
import tempfile

import click

from solosis.utils.logging_utils import debug, log
from solosis.utils.lsf_utils import lsf_job, submit_lsf_job_array
from solosis.utils.state import execution_uid, logger


@lsf_job(mem=64000, cpu=4, queue="normal", time="12:00")
@click.command("merge-h5ad")
@click.option("--samplefile", required=True, help="Sample file text file")
@click.option(
    "--merged_filename", required=True, help="Output file name, e.g., merged.h5ad"
)
@click.option(
    "--job_name",
    required=False,
    type=str,
    default="merge_h5ad",
    help="Optional name for the LSF job. Defaults to merge_h5ad_<uid>.",
)
@debug
@log
def cmd(
    samplefile,
    merged_filename,
    job_name,
    mem,
    cpu,
    queue,
    gpu,
    gpumem,
    gpunum,
    gpumodel,
    time,
    debug,
    **kwargs,
):
    """
    Submit a job to merge multiple h5ad objects into a single file.

    Input samplefile should have 3 mandatory columns:
    1st column: sanger_id, 2nd column: sample_name, 3rd column: irods path

    Make sure to run `solosis-cli sc-rna scanpy --samplefile ...` first.
    """
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

    # Path to the shell script
    shell_script = os.path.abspath(
        os.path.join(os.getenv("SCRIPT_BIN"), "scrna/merge-h5ad/submit.sh")
    )

    if not os.path.exists(shell_script):
        logger.error(f"Shell script not found: {shell_script}")
        return

    # Construct command
    command_str = f"{shell_script} {samplefile} {merged_filename}"

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
        gpunum=gpunum,
        gpumodel=gpumodel,
    )


if __name__ == "__main__":
    cmd()
