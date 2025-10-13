import logging
import os
import tempfile

import click

from solosis.utils.input_utils import process_metadata_file
from solosis.utils.logging_utils import debug, log
from solosis.utils.lsf_utils import lsf_job, submit_lsf_job_array
from solosis.utils.state import execution_uid, logger

########
conda_env = "/software/cellgen/team298/shared/envs/hlb-conda/rna"
sc_base1_path = os.path.abspath(
    os.path.join(
        os.getenv("NOTEBOOKS_DIR"),
        "sc_base1.ipynb",
    )
)
########


@lsf_job(mem=64000, cpu=4, queue="normal", time="12:00")
@click.command("scanpy")
@click.option("--metadata", required=True, help="metadata csv file")
@click.option(
    "--job_name",
    required=False,
    type=str,
    default="scanpy",
    help="Optional name for the LSF job. Defaults to scanpy_<uid>.",
)
@debug
@log
def cmd(metadata, job_name, mem, cpu, queue, gpu, time, debug, **kwargs):
    """
    Submit Scanpy workflow for scRNA-seq data as a job on the compute farm.

    Input samplefile should have 3 mandatory columns:
    1st column: sample_id, 2nd column: sanger_id, 3rd column: cellranger_dir
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
        metadata, required_columns={"sample_id", "cellranger_dir", "sanger_id"}
    )

    valid_samples = []
    for sample in samples:
        sample_id = sample["sample_id"]
        sanger_id = sample["sanger_id"]
        cellranger_dir = sample["cellranger_dir"]
        if not os.path.exists(cellranger_dir):
            logger.error(
                f"Cellranger path does not exist: {cellranger_dir} for sample: {sample_id}. Skipping."
            )
            continue  # skip this sample entirely

        # Path of the expected output notebook
        output_dir = os.path.join(os.getenv("TEAM_SAMPLES_DIR"), sample_id)
        os.makedirs(output_dir, exist_ok=True)
        scanpy_output = os.path.join(output_dir, f"{sample_id}_{sanger_id}.ipynb")
        if os.path.exists(scanpy_output):
            logger.warning(
                f"Notebook for {sample_id} already exists at {scanpy_output}. Skipping."
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

    with tempfile.NamedTemporaryFile(
        delete=False, mode="w", suffix=".txt", dir=os.environ["TEAM_TMP_DIR"]
    ) as tmpfile:
        logger.debug(f"Temporary command file created: {tmpfile.name}")
        os.chmod(tmpfile.name, 0o660)
        for sample in valid_samples:
            sample_id = sample["sample_id"]
            sanger_id = sample["sanger_id"]
            cellranger_dir = sample["cellranger_dir"]
            output_dir = sample["output_dir"]

            # Build papermill command
            command = (
                f"module load cellgen/conda && "
                f"source activate {conda_env} && "
                f"papermill {sc_base1_path} "
                f"{scanpy_output} "
                f"-p samples_database '{os.getenv('TEAM_SAMPLES_DIR')}' "
                f"-p sample_name '{sample_id}' "
                f"-p sanger_id '{sanger_id}' "
                f"-p cellranger_folder '{cellranger_dir}' "
                "--log-output"
            )
            tmpfile.write(command + "\n")

    submit_lsf_job_array(
        command_file=tmpfile.name,
        job_name="scanpy_job_array",
        cpu=cpu,
        mem=mem,
        queue=queue,
        gpu=gpu,
    )


if __name__ == "__main__":
    cmd()
