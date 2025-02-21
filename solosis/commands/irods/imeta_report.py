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
            f"No samples provided. Use --sample or --samplefile options",
            "error",
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

    # Iterate over the samples and run the subprocess for each sample
    for sample in samples:
        secho(f"Processing sample: {sample}", "info")

        # Path to the script
        imeta_report_script = os.path.abspath(
            os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                "../../../bin/irods/imeta-report.sh",
            )
        )

        try:
            result = subprocess.run(
                [
                    imeta_report_script,
                    sample,  # Pass the single sample ID as an argument
                ],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            secho(f"Standard Output: {result.stdout}", "info")
        except subprocess.CalledProcessError as e:
            # Capture and report errors from the subprocess
            secho(f"Error during execution for sample {sample}: {e.stderr}", "error")
        except Exception as e:
            # Catch any unexpected errors
            secho(f"Unexpected error: {str(e)}", "error")


if __name__ == "__main__":
    cmd()
