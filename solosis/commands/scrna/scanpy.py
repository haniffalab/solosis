import logging
import os
import tempfile

import click

from solosis.utils.input_utils import process_metadata_file
from solosis.utils.logging_utils import debug, log
from solosis.utils.lsf_utils import lsf_job, submit_lsf_job_array
from solosis.utils.state import execution_uid, logger

##maybe add in validation with `from solosis.utils.input_utils import collect_samples`


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
    job_name = execution_uid if job_name == "default" else f"{job_name}_{execution_uid}"
    logger.debug(f"Job name: {job_name}")

    samples = process_metadata_file(
        metadata, required_columns={"sample_id", "cellranger_dir"}
    )

    valid_samples = []
    for sample in samples:
        sample_id = sample["sample_id"]
        cellranger_dir = sample["cellranger_dir"]
        output_dir = os.path.join(
            os.getenv("TEAM_SAMPLES_DIR"), sample_id, "cellranger"
        )
        os.makedirs(output_dir, exist_ok=True)

        # Validate irods path
        if validate_cellranger_dir(sample_id, cellranger_dir):
            valid_samples.append(
                {
                    "sample_id": sample_id,
                    "cellranger_dir": cellranger_dir,
                    "output_dir": output_dir,
                }
            )
        else:
            logger.warning(
                f"Unable to validate cellranger path {sample['cellranger_dir']} for sample {sample['sample_id']}. Run `iget-cellranger` cmd before re-trying."
            )

    if not valid_samples:
        logger.error(f"No valid samples found. Exiting")
        return

    # Path to the shell script
    scanpy_shell_script = os.path.abspath(
        os.path.join(
            os.getenv("SCRIPT_BIN"),
            "scrna/scanpy/submit.sh",
        )
    )

    with tempfile.NamedTemporaryFile(
        delete=False, mode="w", suffix=".txt", dir=os.environ["TEAM_TMP_DIR"]
    ) as tmpfile:
        logger.debug(f"Temporary command file created: {tmpfile.name}")
        os.chmod(tmpfile.name, 0o660)
        for sample in valid_samples:
            command = f"{scanpy_shell_script} {sample['sample_id']} {sample['output_dir']} {sample['cellranger_dir']} {version} {cpu} {mem}"
            if sample_basedir:
                command += f" --sample_basedir {sample_basedir}"
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
