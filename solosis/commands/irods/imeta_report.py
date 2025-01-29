import os
import subprocess
import sys
import time

import click
import pandas as pd

from solosis.utils import echo_lsf_submission_message, echo_message, irods_validation


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
    echo_message(
        f"Starting Process: {click.style(ctx.command.name, bold=True, underline=True)}",
        "info",
    )

    # Call the function
    irods_validation()

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
                echo_message(
                    f"Unsupported file format. Please provide a .csv or .tsv file",
                    "error",
                )
                return

            df = pd.read_csv(samplefile, sep=sep)

            if "sample_id" in df.columns:
                samples.extend(df["sample_id"].dropna().astype(str).tolist())
            else:
                echo_message(
                    f"File must contain a 'sample_id' column",
                    "error",
                )
                return
        except Exception as e:
            echo_message(
                f"Error reading sample file: {e}",
                "error",
            )
            return

    if not samples:
        echo_message(
            f"no samples provided. Use `--sample` or `--samplefile`",
            "error",
        )
        return

    # Get the sample data directory from the environment variable
    team_sample_data_dir = os.getenv("TEAM_SAMPLE_DATA_DIR")

    if not team_sample_data_dir:
        echo_message(
            f"TEAM_SAMPLE_DATA_DIR environment variable is not set",
            "error",
        )
        return

    if not os.path.isdir(team_sample_data_dir):
        echo_message(
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
            if overwrite:
                echo_message(
                    f"Overwriting existing outputs for sample '{sample}' in {cellranger_path}.",
                    "warn",
                )
                try:
                    # Remove the directory and its contents
                    # subprocess.run(["rm", "-rf", cellranger_path], check=True)
                    echo_message(
                        f"[DRY RUN] Would remove directory: '{cellranger_path}'.",
                        "info",
                    )
                except subprocess.CalledProcessError as e:
                    echo_message(
                        f"Failed to remove existing directory '{cellranger_path}': {e.stderr}",
                        "error",
                    )
                    return
                samples_to_download.append(sample)
            else:
                echo_message(
                    f"Cellranger outputs already downloaded for sample '{sample}' in {cellranger_path}. Skipping download.",
                    "warn",
                )
        else:
            samples_to_download.append(sample)

    # Confirm samples to download
    if samples_to_download:
        sample_list = "\n".join(
            f"  {idx}. {sample}" for idx, sample in enumerate(samples_to_download, 1)
        )
        echo_message(
            f"Samples for download:\n{sample_list}",
            "info",
        )
    else:
        echo_message(
            f"All provided samples already have sanger processed cellranger outputs. No downloads required.",
            "warn",
        )
        return  # Exit if no samples need downloading

    # Join all sample to download IDs into a single string, separated by commas
    sample_ids = ",".join(samples_to_download)

    # Path to the script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    pull_cellranger_script = os.path.abspath(
        os.path.join(script_dir, "../../../bin/irods/iget-cellranger/submit.sh")
    )

    # Construct the command
    cmd = [
        pull_cellranger_script,
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
        echo_lsf_submission_message(result.stdout)
    except subprocess.CalledProcessError as e:
        echo_message(
            f"Error during execution: {e.stderr}",
            "error",
        )


if __name__ == "__main__":
    cmd()
