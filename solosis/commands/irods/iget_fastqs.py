import os
import subprocess
import sys
import time
from datetime import datetime

import click
import pandas as pd

from solosis.utils.env_utils import irods_auth
from solosis.utils.logging_utils import secho

FASTQ_EXTENSIONS = [".fastq", ".fastq.gz"]


@click.command("iget-fastqs")
@click.option("--sample", type=str, help="Sample ID (string)")
@click.option(
    "--samplefile",
    type=click.Path(exists=True),
    help="Path to a CSV or TSV file containing sample IDs",
)
@click.pass_context
def cmd(ctx, sample, samplefile):
    """
    Downloads fastqs from iRODS...

    Utilising NF-irods-to-fastq pipeline developed by Cellgeni.
    Pulled directly from Github repo- up-to-date.
    """
    secho(
        f"Starting Process: {click.style(ctx.command.name, bold=True, underline=True)}",
        "info",
    )

    # Call the function
    irods_auth()

    samples = []

    # Collect sample IDs from the provided options
    if sample:
        samples.append(sample)

    # Read sample IDs from a file if provided
    if samplefile:
        try:
            sep = (
                ","
                if samplefile.endswith(".csv")
                else "\t" if samplefile.endswith(".tsv") else None
            )
            if sep is None:
                secho(
                    f"unsupported file format. Please provide a .csv or .tsv file",
                    "error",
                )
                return

            df = pd.read_csv(samplefile, sep=sep)

            if "sample_id" in df.columns:
                samples.extend(df["sample_id"].dropna().astype(str).tolist())
            else:
                secho(
                    f"file must contain a 'sample_id' column",
                    "error",
                )
                return
        except Exception as e:
            secho(
                f"error reading sample file: {e}",
                "error",
            )
            return

    if not samples:
        secho(
            f"no samples provided. Use `--sample` or `--samplefile`",
            "error",
        )
        secho(
            f"try using `solosis-cli irods iget-fastqs --help`",
            "info",
        )
        return

    # Get the sample data directory from the environment variable
    team_data_dir = os.getenv("TEAM_DATA_DIR")
    if not team_data_dir:
        secho(
            f"TEAM_DATA_DIR environment variable is not set",
            "error",
        )
        return

    samples_dir = os.path.join(team_data_dir, "samples")
    if not os.path.isdir(samples_dir):
        secho(
            f"sample data directory '{samples_dir}' does not exist",
            "error",
        )
        return

    # Check each sample
    samples_to_download = []
    for sample in samples:
        # Path where FASTQ files are expected for each sample
        fastq_path = os.path.join(samples_dir, sample, "fastq")

        # Check if FASTQ files exist in the directory for the sample
        if os.path.exists(fastq_path) and any(
            f.endswith(ext) for ext in FASTQ_EXTENSIONS for f in os.listdir(fastq_path)
        ):
            secho(
                f"FASTQ files already found for sample '{sample}' in {fastq_path}. Skipping download.",
                "warn",
            )
        else:
            samples_to_download.append(sample)

    # Inform if there are samples that need FASTQ downloads
    if samples_to_download:
        secho(
            f"samples without FASTQ files: {samples_to_download}",
            "progress",
        )
    else:
        secho(
            f"all provided samples already have FASTQ files. No downloads required.",
            "warn",
        )
        return  # Exit if no samples need downloading

    # Join all sample to download IDs into a single string, separated by commas
    sample_ids = ",".join(samples_to_download)

    # Path to the script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    irods_to_fastq_script = os.path.abspath(
        os.path.join(script_dir, "../../../bin/irods/iget-fastqs/submit.sh")
    )

    # Construct the command with optional BAM flag
    cmd = [
        irods_to_fastq_script,
        sample_ids,
    ]

    # Print the command being executed for debugging
    secho(
        f"executing command: {' '.join(cmd)}",
        "progress",
    )

    # Execute the command with an active spinner
    secho(
        f"starting process for samples: {sample_ids}...",
        "progress",
    )

    # Execute the command and stream the output
    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        # Process stdout in real-time
        for line in process.stdout:
            timestamp = datetime.now().strftime("%H:%M:%S")
            secho(f"[{timestamp}] {line.strip()}", "progress")

        # Process stderr in real-time
        for line in process.stderr:
            timestamp = datetime.now().strftime("%H:%M:%S")
            secho(f"[{timestamp}] {line.strip()}", "warn")

        process.wait()
        if process.returncode != 0:
            secho(f"error during execution. Return code: {process.returncode}", "error")
        else:
            secho("process completed successfully.", "success")
    except Exception as e:
        secho(f"error executing command: {e}", "error")


if __name__ == "__main__":
    cmd()
