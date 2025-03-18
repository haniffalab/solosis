import logging
import os
import secrets
import tempfile

import click

from solosis.utils.env_utils import irods_auth
from solosis.utils.input_utils import collect_samples
from solosis.utils.logging_utils import debug
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
        logger.warning("All samples already processed.")
        raise click.Abort()

    with tempfile.NamedTemporaryFile(
        delete=False, mode="w", suffix=".txt", dir=os.environ["TEAM_TMP_DIR"]
    ) as tmpfile:
        logger.info(f"Temporary command file created: {tmpfile.name}")
        os.chmod(tmpfile.name, 0o660)
        for sample in samples_to_download:
            tmpfile.write(sample + "\n")

    # Run the metadata script first
    random_id = secrets.token_hex(4)
    metadata_script = os.path.abspath(
        os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "../../../bin/irods/nf-irods-to-fastq-metadata.sh",
        )
    )
    popen([metadata_script, tmpfile.name, random_id])

    # Define expected TSV file path
    metadata_tsv_path = os.path.join(
        os.getenv("TEAM_TMP_DIR"), random_id, "metadata", "metadata.tsv"
    )

    logger.error(metadata_tsv_path)
    click.Abort()

    # Check if metadata TSV file exists
    if not os.path.exists(metadata_tsv_path):
        logger.error(f"Metadata TSV file '{metadata_tsv_path}' not found.")
        raise click.Abort()

    # Read and validate TSV file
    valid_samples = []
    try:
        with open(metadata_tsv_path, "r") as tsv_file:
            for line in tsv_file:
                columns = line.strip().split("\t")
                if len(columns) < 2:
                    logger.warning(f"Skipping malformed line: {line.strip()}")
                    continue

                sample_id, status = columns[0], columns[1]
                if status.lower() == "valid":
                    valid_samples.append(sample_id)
                else:
                    logger.warning(
                        f"Skipping sample '{sample_id}' due to invalid status."
                    )

    except Exception as e:
        logger.error(f"Error reading metadata TSV file: {e}")
        raise click.Abort()

    # Filter only valid samples for download
    samples_to_download = [s for s in samples_to_download if s in valid_samples]

    if not samples_to_download:
        logger.warning("No valid samples available for download.")
        raise click.Abort()

    # Run the actual fastq download script
    fastq_script = os.path.abspath(
        os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "../../../bin/irods/nf-irods-to-fastq.sh",
        )
    )
    popen([fastq_script, tmpfile.name])


if __name__ == "__main__":
    cmd()
