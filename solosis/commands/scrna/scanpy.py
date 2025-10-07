import logging
import os
import tempfile

import click

from solosis.utils.input_utils import process_h5_file
from solosis.utils.logging_utils import debug, log
from solosis.utils.lsf_utils import lsf_job, submit_lsf_job_array
from solosis.utils.state import execution_uid, logger

conda_env = "/software/cellgen/team298/shared/envs/solosis-sc-env"

base = os.getenv(
    "SOLOSIS_BASE", os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
)
NOTEBOOK_PATH = os.path.join(base, "notebooks", "sc_base1.ipynb")


@lsf_job(mem=64000, cpu=4, queue="normal", time="12:00")
@click.command("scanpy")
@click.option("--metadata", required=True, help="metadata csv file")
@click.option(
    "--sample_basedir",
    required=False,
    default="/lustre/scratch124/cellgen/haniffa/data/samples",
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
    metadata, sample_basedir, job_name, mem, cpu, queue, gpu, time, debug, **kwargs
):
    """
    Submit Scanpy workflow for scRNA-seq data as a job on the compute farm.

    Input samplefile should have 3 mandatory columns:
    1st column: sample_id, 2nd column: sanger_id, 3rd column: h5_path
    """
    if debug:
        logger.setLevel(logging.DEBUG)

    ctx = click.get_current_context()
    logger.debug(
        f"Starting command: {click.style(ctx.command.name, bold=True, underline=True)}"
    )
    job_name = execution_uid if job_name == "default" else f"{job_name}_{execution_uid}"
    logger.debug(f"Job name: {job_name}")

    samples = process_h5_file(
        metadata, required_columns={"sample_id", "h5_path", "sanger_id"}
    )
    invalid = [s["h5_path"] for s in samples if not s["h5_path"].endswith(".h5")]
    if invalid:
        # Stop everything — don’t proceed to submission
        raise click.ClickException(
            f"Invalid h5_path(s) detected (must end with .h5):\n" + "\n".join(invalid)
        )

    valid_samples = []
    for sample in samples:
        sample_id = sample["sample_id"]
        h5_path = sample["h5_path"]
        if not os.path.exists(h5_path):
            logger.error(
                f"h5 file does not exist: {h5_path} for sample: {sample_id}. Skipping."
            )
            continue  # skip this sample entirely

        sanger_id = sample.get("sanger_id") or sample["sample_id"]
        output_dir = os.path.join(os.getenv("TEAM_SAMPLES_DIR"), sample_id)
        os.makedirs(output_dir, exist_ok=True)

        # Path of the expected output notebook
        scanpy_output = os.path.join(output_dir, f"{sample_id}_{sanger_id}.ipynb")

        if os.path.exists(scanpy_output):
            logger.warning(
                f"Notebook for {sample_id} already exists at {scanpy_output}. Skipping."
            )
            continue

        valid_samples.append(
            {
                "sample_id": sample_id,
                "sanger_id": sanger_id,
                "h5_path": h5_path,
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
            h5_path = sample["h5_path"]
            output_dir = sample["output_dir"]

            # Build papermill command
            command = (
                f"module load cellgen/conda && "
                f"source activate {conda_env} && "
                f"papermill {NOTEBOOK_PATH} "
                f"{output_dir}/{sample_id}_{sanger_id}.ipynb "
                f"-p samples_database '{sample_basedir}' "
                f"-p sample_name '{sanger_id}' "
                f"-p sample_id '{sample_id}' "
                f'-p h5_file "{h5_path}" '
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
