import logging
import os
import tempfile

import click
import pandas as pd

from solosis.utils.env_utils import irods_auth
from solosis.utils.input_utils import process_metadata_file, validate_irods_path
from solosis.utils.logging_utils import debug, log
from solosis.utils.lsf_utils import lsf_job, submit_lsf_job_array
from solosis.utils.state import logger


@lsf_job(mem=4000, cpu=2, queue="small", time="12:00")
@click.command("iget-cellranger")
@click.option(
    "--metadata",
    type=click.Path(exists=True),
    help="Path to a CSV or TSV file containing metadata",
)
@debug
@log
def cmd(
    metadata,
    mem,
    cpu,
    queue,
    gpu,
    gpumem,
    time,
    debug,
):
    """Downloads cellranger outputs from iRODS."""
    if debug:
        logger.setLevel(logging.DEBUG)

    ctx = click.get_current_context()
    logger.debug(
        f"Starting command: {click.style(ctx.command.name, bold=True, underline=True)}"
    )

    if not irods_auth():
        raise click.Abort()

    samples = process_metadata_file(
        metadata, required_columns={"sample_id", "irods_path"}
    )

    valid_samples = []
    for sample in samples:
        sample_id = sample["sample_id"]
        irods_path = sample["irods_path"]
        output_dir = os.path.join(
            os.getenv("TEAM_SAMPLES_DIR"), sample_id, "cellranger"
        )
        os.makedirs(output_dir, exist_ok=True)

        # Validate irods path
        if validate_irods_path(sample_id, irods_path):
            valid_samples.append(
                {
                    "sample_id": sample_id,
                    "irods_path": irods_path,
                    "output_dir": output_dir,
                }
            )
        else:
            logger.warning(
                f"Unable to validate iRODs path {sample['irods_path']} for sample {sample['sample_id']}. Skipping this sample"
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
            command = (
                f"iget -r {irods_path} {output_dir} ; "
                f"chmod -R g+w {output_dir} >/dev/null 2>&1 || true"
            )
            tmpfile.write(command + "\n")

    submit_lsf_job_array(
        command_file=tmpfile.name,
        job_name="iget_cellranger_job_array",
        cpu=cpu,
        mem=mem,
        queue=queue,
        gpu=gpu,
        gpumem=gpumem,
    )


if __name__ == "__main__":
    cmd()
