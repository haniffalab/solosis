import click

from solosis.utils.logging_utils import debug, log
from solosis.utils.lsf_utils import lsf_job, submit_lsf_job
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
def cmd(notebook, job_name, mem, cpu, queue, gpu, time, debug, **kwargs):
    """Submit a Jupyter notebook to run via LSF"""
    job_name = execution_uid if job_name == "default" else f"{job_name}_{execution_uid}"
    command_to_exec = (
        f"source ~/.bashrc && "
        f"conda activate /software/cellgen/team298/shared/envs/hl-conda/hl_minimal_v1.0.0 && "
        f"jupyter nbconvert --to notebook --execute {notebook}"
    )
    logger.info(f"Job name: {job_name} submitted to queue: {queue}")
    submit_lsf_job(
        command=command_to_exec,
        job_name=job_name,
        mem=mem,
        cpu=cpu,
        queue=queue,
        gpu=gpu,
        execution_uid=execution_uid,
    )


if __name__ == "__main__":
    cmd()
