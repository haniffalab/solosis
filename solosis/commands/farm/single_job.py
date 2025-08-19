import click

from solosis.utils.logging_utils import debug, log
from solosis.utils.lsf_utils import lsf_job, submit_lsf_job
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
    if not command_to_exec:
        logger.error("No command to execute")
        return

    # Convert tuple of strings to a single string
    command_str = " ".join(command_to_exec)

    # Ensure all kwargs are strings for environment variables
    env_vars = {str(k): str(v) for k, v in kwargs.items()}

    # Compose job name
    job_name = execution_uid if job_name == "default" else f"{job_name}_{execution_uid}"
    logger.info(f"Job name: {job_name} submitted to queue: {queue}")

    # Submit the job
    submit_lsf_job(
        command=command_str,
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
