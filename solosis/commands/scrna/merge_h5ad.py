import logging
import os
import tempfile

import click

from solosis.utils.input_utils import process_metadata_file
from solosis.utils.logging_utils import debug, log
from solosis.utils.lsf_utils import lsf_job, submit_lsf_job_array
from solosis.utils.state import execution_uid, logger

# Define the environment
conda_env = "/software/cellgen/team298/shared/envs/solosis-sc-env"
rna__merge_path = os.path.abspath(
    os.path.join(
        os.getenv("NOTEBOOKS_DIR"),
        "rna__merge.ipynb",
    )
)


@lsf_job(mem=64000, cpu=4, queue="normal", time="12:00")
@click.command("merge-h5ad")
@click.option("--metadata", required=True, help="metadata csv file")
@click.option(
    "--merged_filename", required=True, help="Output file name, e.g. merged.h5ad"
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
    metadata,
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

    Input metadata should have 3 mandatory columns:
    1st column: sample_id
    2nd column: sanger_id
    3rd column: h5_path

    Make sure to run `solosis-cli sc-rna scanpy --metadata ...` first.
    """
    if debug:
        logger.setLevel(logging.DEBUG)

    ctx = click.get_current_context()
    logger.debug(
        f"Starting command: {click.style(ctx.command.name, bold=True, underline=True)}"
    )
    job_name = execution_uid if job_name == "default" else f"{job_name}_{execution_uid}"
    logger.debug(f"Job name: {job_name}")

    samples = process_metadata_file(
        metadata,
        required_columns={"sample_id", "sanger_id", "h5_path"},
    )

    # Check for invalid h5 paths
    for s in samples:
        h5_path = s["h5_path"]
        if not h5_path.endswith(".h5"):
            raise click.ClickException(
                f"Invalid h5_path detected (must end with .h5): {h5_path}"
            )

    # Define output path for notebook
    # Note: there is only a single notebook generated for all samples
    output_notebook = os.path.join(
        os.getenv("TEAM_SAMPLES_DIR"), f"merged_objects", f"{merged_filename}.ipynb"
    )

    valid_samples = []
    # Normally, we would validate samples and then pass those downstream.
    # However, this notebook is setup to receive just the path to the metadata
    # file. Therefore, we offload any validation for this command to the notebook.

    with tempfile.NamedTemporaryFile(
        delete=False, mode="w", suffix=".txt", dir=os.environ["TEAM_TMP_DIR"]
    ) as tmpfile:
        logger.debug(f"Temporary command file created: {tmpfile.name}")
        os.chmod(tmpfile.name, 0o660)

        # Build papermill command
        command = (
            f"module load cellgen/conda && "
            f"source activate {conda_env} && "
            f"papermill {rna__merge_path} {output_notebook} "
            f"-p metadata '{metadata}' "
            f"-p merged_filename '{merged_filename}' "
            f"-p samples_database '{os.getenv('TEAM_SAMPLES_DIR')}' "
            f"-k solosis-sc-env"
        )
        tmpfile.write(command + "\n")

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
