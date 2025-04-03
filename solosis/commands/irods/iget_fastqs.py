import logging
import os
import secrets
import tempfile

import click
import pandas as pd

from solosis.utils.env_utils import irods_auth
from solosis.utils.input_utils import collect_samples, validate_library_type
from solosis.utils.logging_utils import debug, log
from solosis.utils.lsf_utils import lsf_job, submit_lsf_job_array
from solosis.utils.state import logger
from solosis.utils.subprocess_utils import popen

FASTQ_EXTENSIONS = [".fastq", ".fastq.gz"]


@lsf_job(mem=4000, cpu=2, queue="small")
@click.command("iget-fastqs")
@click.option("--sample", type=str, help="Sample ID (string)")
@click.option(
    "--samplefile",
    type=click.Path(exists=True),
    help="Path to a CSV or TSV file containing sample IDs",
)
@debug
@log
def cmd(sample, samplefile, mem, cpu, queue, gpu, debug):
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
        logger.debug(f"Temporary command file created: {tmpfile.name}")
        os.chmod(tmpfile.name, 0o660)
        for sample in samples_to_download:
            tmpfile.write(sample + "\n")

    # Run the metadata script first
    logger.info(f"Looking for data in global archive")
    random_id = secrets.token_hex(4)
    metadata_script = os.path.abspath(
        os.path.join(
            os.getenv("SCRIPT_BIN"),
            "irods/nf-irods-to-fastq-metadata.sh",
        )
    )
    popen([metadata_script, tmpfile.name, random_id])

    # Define expected TSV file path
    metadata_tsv_path = os.path.join(
        os.getenv("TEAM_TMP_DIR"), random_id, "metadata", "metadata.tsv"
    )

    # Check if metadata TSV file exists
    if not os.path.exists(metadata_tsv_path):
        logger.error(f"Metadata TSV file {metadata_tsv_path} not found.")
    else:
        logger.info(f"Metadata TSV file saved: {metadata_tsv_path}")

        # Read and validate TSV file
        validate_library_type(metadata_tsv_path)

        # Run the iRODS to FASTQ script
        irods_to_fastq_script = os.path.abspath(
            os.path.join(
                os.getenv("SCRIPT_BIN"),
                "irods/nf-irods-to-fastq.sh",
            )
        )
        popen([irods_to_fastq_script, tmpfile.name])

    logger.info(f"Looking for data in team archive")
    with tempfile.NamedTemporaryFile(
        delete=False, mode="w", suffix=".txt", dir=os.environ["TEAM_TMP_DIR"]
    ) as tmpfile:
        logger.debug(f"Temporary command file created: {tmpfile.name}")
        os.chmod(tmpfile.name, 0o660)
        for sample in samples_to_download:
            sample_dir = os.path.join(os.getenv("TEAM_SAMPLES_DIR"), sample)
            report_path = os.path.join(sample_dir, "imeta_report.csv")
            fastq_path = os.path.join(sample_dir, "fastq")

            imeta_report_script = os.path.abspath(
                os.path.join(
                    os.getenv("SCRIPT_BIN"),
                    "irods/imeta_report.sh",
                )
            )
            popen([imeta_report_script, sample, report_path])

            if os.path.exists(report_path):
                df = pd.read_csv(
                    report_path, header=None, names=["collection_type", "path"]
                )

                filtered_df = df[
                    (df["collection_type"] == "COLLECTION")
                    & (df["path"].str.startswith("/archive/team298"))
                ]

                for _, row in filtered_df.iterrows():
                    path = row["path"]
                    command = f"iget -r {path} {sample_dir} ; chmod -R g+w {fastq_path} >/dev/null 2>&1 || true"
                    tmpfile.write(command + "\n")
                    logger.info(
                        f'FASTQ files for sample "{sample}" will be downloaded to: {fastq_path}'
                    )

    if os.path.getsize(tmpfile.name) > 0:
        submit_lsf_job_array(
            command_file=tmpfile.name,
            job_name="iget_fastqs_job_array",
            cpu=cpu,
            mem=mem,
            queue=queue,
        )


if __name__ == "__main__":
    cmd()
