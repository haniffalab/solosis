import logging
import os
import subprocess
import tempfile
from datetime import datetime

import click

from solosis.utils.env_utils import irods_auth
from solosis.utils.input_utils import collect_samples
from solosis.utils.logging_utils import debug, secho
from solosis.utils.state import logger
from solosis.utils.subprocess_utils import popen

FASTQ_EXTENSIONS = [".fastq", ".fastq.gz"]


@debug
@click.command("iget-fastqs")
@click.option("--sample", type=str, help="Sample ID (string)")
@click.option(
    "--samplefile",
    type=click.Path(exists=True),
    help="Path to a CSV or TSV file containing sample IDs",
)
def cmd(sample, samplefile, debug):
    """Downloads fastqs from iRODS."""
    if debug:
        logger.setLevel(logging.DEBUG)

    ctx = click.get_current_context()
    logger.debug(
        f"Starting command: {click.style(ctx.command.name, bold=True, underline=True)}"
    )

    if not irods_auth():
        raise click.Abort()

    samples = collect_samples(sample, samplefile)
    samples_to_download = []
    for sample in samples:
        fastq_path = os.path.join(os.getenv("TEAM_SAMPLES_DIR"), sample, "fastq")
        if os.path.exists(fastq_path) and any(
            f.endswith(ext) for ext in FASTQ_EXTENSIONS for f in os.listdir(fastq_path)
        ):
            logger.warning(
                f"FASTQ files already found for sample '{sample}' in {fastq_path}. Skipping download."
            )
        else:
            samples_to_download.append(sample)

    if not samples_to_download:
        logger.warning(f"All samples already proccessed.")
        raise click.Abort()

    with tempfile.NamedTemporaryFile(
        delete=False, mode="w", suffix=".txt", dir=os.environ["TEAM_TMP_DIR"]
    ) as tmpfile:
        logger.info(f"Temporary command file created: {tmpfile.name}")
        os.chmod(tmpfile.name, 0o660)
        for sample in samples_to_download:
            tmpfile.write(sample + "\n")

    irods_to_fastq_script = os.path.abspath(
        os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "../../../bin/irods/nf-irods-to-fastq.sh",
        )
    )
    popen([irods_to_fastq_script, tmpfile.name])


if __name__ == "__main__":
    cmd()
