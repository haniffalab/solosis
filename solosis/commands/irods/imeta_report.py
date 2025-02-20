import os
import subprocess
import sys
import time

import click
import pandas as pd

from solosis.utils.env_utils import irods_auth
from solosis.utils.logging_utils import secho


# change to pull-cellranger
@click.command("imeta-report")
@click.option("--sample", type=str, help="Sample ID (string).")
@click.option(
    "--samplefile",
    type=click.Path(exists=True),
    help="Path to a CSV or TSV file containing sample IDs.",
)
def cmd(sample, samplefile):
    """
    Generates report of data available on iRODS
    """
    ctx = click.get_current_context()
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
                    f"Unsupported file format. Please provide a .csv or .tsv file",
                    "error",
                )
                return

            df = pd.read_csv(samplefile, sep=sep)

            if "sample_id" in df.columns:
                samples.extend(df["sample_id"].dropna().astype(str).tolist())
            else:
                secho(
                    f"File must contain a 'sample_id' column",
                    "error",
                )
                return
        except Exception as e:
            secho(
                f"Error reading sample file: {e}",
                "error",
            )
            return

    if not samples:
        secho(
            f"no samples provided. Use `--sample` or `--samplefile`",
            "error",
        )
        return

    # Get the sample data directory from the environment variable
    team_sample_data_dir = os.getenv("TEAM_SAMPLE_DATA_DIR")

    if not team_sample_data_dir:
        secho(
            f"TEAM_SAMPLE_DATA_DIR environment variable is not set",
            "error",
        )
        return

    if not os.path.isdir(team_sample_data_dir):
        secho(
            f"Sample data directory '{team_sample_data_dir}' does not exist",
            "error",
        )
        return

    # Check each sample
    samples_to_download = []
    for sample in samples:
        # Path where cellranger outputs are expected for each sample
        cellranger_path = os.path.join(team_sample_data_dir, sample, "cellranger")

        # Check if output exists
        if os.path.exists(cellranger_path):
            samples_to_download.append(sample)
        else:
            secho(
                f"Overwriting existing outputs for sample '{sample}' in {cellranger_path}.",
                "warn",
            )

    # Confirm samples to download
    if samples_to_download:
        sample_list = "\n".join(
            f"  {idx}. {sample}" for idx, sample in enumerate(samples_to_download, 1)
        )
        secho(
            f"Samples for download:\n{sample_list}",
            "info",
        )
    else:
        secho(
            f"All provided samples already have sanger processed cellranger outputs. No downloads required.",
            "warn",
        )
        return  # Exit if no samples need downloading

    # Join all sample to download IDs into a single string, separated by commas
    sample_ids = ",".join(samples_to_download)

    # Path to the script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    imeta_report_script = os.path.abspath(
        os.path.join(script_dir, "../../../bin/irods/imeta-report/submit.sh")
    )

    # Construct the command
    cmd = [
        imeta_report_script,
        sample_ids,
    ]

    try:
        result = subprocess.run(
            cmd,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
    except subprocess.CalledProcessError as e:
        secho(
            f"Error during execution: {e.stderr}",
            "error",
        )


if __name__ == "__main__":
    cmd()
