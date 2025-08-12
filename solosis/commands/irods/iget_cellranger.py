import logging
import os
import tempfile

import click
import pandas as pd

from solosis.utils.env_utils import irods_auth
from solosis.utils.input_utils import process_irods_samplefile, validate_irods_path
from solosis.utils.logging_utils import debug, log
from solosis.utils.lsf_utils import lsf_options_sm, submit_lsf_job_array
from solosis.utils.state import logger
from solosis.utils.subprocess_utils import popen


@lsf_options_sm
@click.command("iget-cellranger")
@click.option(
    "--samplefile",
    type=click.Path(exists=True),
    help="columns required 'sample_id','irods_path'. Path to a CSV or TSV file containing sample IDs.",
)
@debug
@log
def cmd(samplefile, mem, cpu, queue, debug):
    """Downloads cellranger outputs from iRODS."""
    if debug:
        logger.setLevel(logging.DEBUG)

    ctx = click.get_current_context()
    logger.debug(
        f"Starting command: {click.style(ctx.command.name, bold=True, underline=True)}"
    )

    if not irods_auth():
        raise click.Abort()

    samples = process_irods_samplefile(samplefile)
    samples_to_download = []

    with tempfile.NamedTemporaryFile(
        delete=False, mode="w", suffix=".txt", dir=os.environ["TEAM_TMP_DIR"]
    ) as tmpfile:
        logger.debug(f"Temporary command file created: {tmpfile.name}")
        os.chmod(tmpfile.name, 0o660)
        for sample in samples:
            sample_id = sample["sample_id"]
            irods_path = sample["irods_path"]

            output_dir = os.path.join(
                os.getenv("TEAM_SAMPLES_DIR"), sample_id, "cellranger"
            )
            os.makedirs(output_dir, exist_ok=True)

            # validate irods path using imeta
            validate_irods_path(sample_id, irods_path)

            command = (
                f"iget -r {irods_path} {output_dir} ; "
                f"chmod -R g+w {output_dir} >/dev/null 2>&1 || true"
            )
            tmpfile.write(command + "\n")

            logger.info(
                f'Collection "{irods_path}" for sample "{sample_id}" will be downloaded to: {output_dir}'
            )

            # appending for the log file later on
            samples_to_download.append((sample_id, irods_path, output_dir))

    submit_lsf_job_array(
        command_file=tmpfile.name,
        job_name="iget_cellranger_job_array",
        cpu=cpu,
        mem=mem,
        queue=queue,
    )

    if samples_to_download:
        log_file = os.path.join(os.getcwd(), "iget-cellranger.log")
        df = pd.DataFrame(
            samples_to_download, columns=["sample", "irods_path", "cellranger_dir"]
        )
        df.to_csv(log_file, index=False)
        logger.info(f"Log file of output paths: {log_file}")


if __name__ == "__main__":
    cmd()
