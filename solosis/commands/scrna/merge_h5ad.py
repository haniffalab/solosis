import logging
import os
import tempfile

import click

from solosis.utils.input_utils import process_metadata_file
from solosis.utils.logging_utils import debug, log
from solosis.utils.lsf_utils import lsf_job, submit_lsf_job_array
from solosis.utils.state import execution_uid, logger

########
conda_env = "/software/cellgen/team298/shared/envs/solosis-sc-env"
# SOLOSIS_DIR = os.getenv("SOLOSIS_BASE") ## wouldn't work without the solosis module loaded

# found this potential solution
base = os.getenv(
    "SOLOSIS_BASE", os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
)
NOTEBOOK_PATH = os.path.join(base, "notebooks", "rna__merge.ipynb")
########


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
    metadata, merged_filename, job_name, mem, cpu, queue, gpu, time, debug, **kwargs
):
    """
    Submit a job to merge multiple h5ad objects into a single file.

    Input metadata should have 3 mandatory columns:
    1st column: sample_id, 2nd column: sanger_id, 3rd column: cellranger_dir

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

    # Path of the expected output notebook
    scanpy_output = os.path.join(output_dir, f"{sample_id}_{sanger_id}.ipynb")

    samples = process_metadata_file(
        metadata, required_columns={"sample_id", "cellranger_dir", "sanger_id"}
    )

    valid_samples = []
    for sample in samples:
        sample_id = sample["sample_id"]
        cellranger_dir = sample["cellranger_dir"]
        if not os.path.exists(cellranger_dir):
            logger.error(
                f"Cellranger path does not exist: {cellranger_dir} for sample: {sample_id}. Skipping."
            )
            continue  # skip this sample entirely

        sanger_id = sample.get("sanger_id") or sample["sample_id"]
        output_dir = os.path.join(os.getenv("TEAM_SAMPLES_DIR"), sample_id)
        os.makedirs(output_dir, exist_ok=True)

        # Path of the expected output notebook
        scanpy_notebook = os.path.join(output_dir, f"{sample_id}_{sanger_id}.ipynb")

        if not os.path.exists(scanpy_output):
            logger.warning(
                f"Notebook for {sample_id} exists at {scanpy_notebook}. Skipping."
            )
            continue  # skip this sample

        valid_samples.append(
            {
                "sample_id": sample_id,
                "sanger_id": sanger_id,
                "cellranger_dir": cellranger_dir,
                "output_dir": output_dir,
            }
        )

    if not valid_samples:
        logger.error(f"No valid samples found. Exiting")
        return

    # Submit the job
    with tempfile.NamedTemporaryFile(
        delete=False, mode="w", suffix=".txt", dir=os.environ["TEAM_TMP_DIR"]
    ) as tmpfile:
        logger.debug(f"Temporary command file created: {tmpfile.name}")
        os.chmod(tmpfile.name, 0o660)
        tmpfile.write(command_str + "\n")
        # Build papermill command
        command = (
            f"module load cellgen/conda && "
            f"source activate {conda_env} && "
            f"papermill {NOTEBOOK_PATH} merge_{merged_filename}.ipynb "
            f"-p sample_table {metadata} "
            f"-p merged_filename {merged_filename} "
            f"-k python3;"
        )
        tmpfile.write(command + "\n")

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
