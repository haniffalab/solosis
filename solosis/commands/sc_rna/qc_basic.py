import os
import subprocess
import sys

import click
import pandas as pd

from solosis.utils import echo_message, log_command

FASTQ_EXTENSIONS = [".fastq", ".fastq.gz"]


@click.command("qc-basic")
@click.option("--sample", type=str, help="Sample ID (string)")
@click.option(
    "--samplefile",
    type=click.Path(exists=True),
    help="Path to a CSV or TSV file containing sample IDs",
)
@click.option(
    "--create-bam",
    is_flag=True,
    default=False,
    help="Generate BAM files for each sample",
)
@click.option(
    "--version",
    type=str,
    default="7.2.0",  # Set a default version
    help="Cell Ranger version to use (e.g., '7.2.0')",
)
@click.pass_context
def cmd(ctx, sample, samplefile, create_bam, version):
    """
    qc-basic
    """
    log_command(ctx)
    echo_message(
        f"Starting Process: {click.style(ctx.command.name, bold=True, underline=True)}",
        "info",
    )

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
                    f"unsupported file format. Please provide a .csv or .tsv file",
                    "error",
                )
                return

            df = pd.read_csv(samplefile, sep=sep)

            if "sample_id" in df.columns:
                samples.extend(df["sample_id"].dropna().astype(str).tolist())
            else:
                echo_message(
                    f"file must contain a 'sample_id' column",
                    "error",
                )
                return
        except Exception as e:
            echo_message(
                f"error reading sample file: {e}",
                "error",
            )
            return

    if not samples:
        echo_message(
            f"no samples provided. Use --sample or --samplefile",
            "error",
        )
        return

    # Get the sample data directory from the environment variable
    team_data_dir = os.getenv("TEAM_DATA_DIR")
    if not team_data_dir:
        echo_message(
            f"TEAM_DATA_DIR environment variable is not set",
            "error",
        )
        return

    samples_dir = os.path.join(team_data_dir, "samples")
    if not os.path.isdir(samples_dir):
        echo_message(
            f"sample data directory '{samples_dir}' does not exist",
            "error",
        )
        return

    valid_samples = []
    for sample in samples:
        cr_path = os.path.join(samples_dir, sample, "cellranger")

        # Check for "filtered_feature_bc_matrix.h5" files
        if os.path.exists(cr_path):
            for subfolder in os.listdir(cr_path):
                subfolder_path = os.path.join(cr_path, subfolder)
                if os.path.isdir(subfolder_path):
                    h5_file_path = os.path.join(
                        subfolder_path, "filtered_feature_bc_matrix.h5"
                    )
                    if os.path.exists(h5_file_path):
                        valid_samples.append(sample)
                        break

    if not valid_samples:
        echo_message(
            f"no valid samples found with FASTQ files. Exiting",
            "error",
        )
        return

    # Join all valid sample IDs into a single string, separated by commas
    sample_ids = ",".join(valid_samples)

    echo_message(
        f"starting qc for samples: {sample_ids}...",
        "progress",
    )


if __name__ == "__main__":
    cmd()
