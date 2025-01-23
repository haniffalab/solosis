import os
import subprocess

import click
import pandas as pd

from solosis.utils import echo_message

FASTQ_EXTENSIONS = [".fastq", ".fastq.gz"]


@click.command("starsolo")
@click.option("--sample", type=str, help="Sample ID (string)")
@click.option(
    "--samplefile",
    type=click.Path(exists=True),
    help="Path to a CSV or TSV file containing sample IDs",
)
def cmd(sample, samplefile):
    """
    STARsolo aligns single-cell RNA sequencing  reads...

    STARsolo (2.7.11b) Aligner processes scRNA seq data to generate
    GEX matrices & identify cell-specific transcripts.

    """
    # Print a clear introductory message
    ctx = click.get_current_context()
    echo_message(
        f"Starting Process: {click.style(ctx.command.name, bold=True, underline=True)}",
        "info",
    )
    echo_message(f"loading starsolo")

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
        fastq_path = os.path.join(samples_dir, sample, "fastq")

        # Check if FASTQ files exist in the directory
        if os.path.exists(fastq_path) and any(
            f.endswith(ext) for ext in FASTQ_EXTENSIONS for f in os.listdir(fastq_path)
        ):
            valid_samples.append(sample)
        else:
            echo_message(
                f"no FASTQ files found for sample {sample} in {fastq_path}. Skipping this sample",
                "warn",
            )

    if not valid_samples:
        echo_message(
            f"no valid samples found with FASTQ files. Exiting",
            "error",
        )
        return

    # Join all valid sample IDs into a single string, separated by commas
    sample_ids = ",".join(valid_samples)

    # Path to the Cell Ranger submission script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    starsolo_submit_script = os.path.abspath(
        os.path.join(script_dir, "../../../bin/alignment/starsolo/submit.sh")
    )

    # Construct the command with optional BAM flag
    cmd = [starsolo_submit_script, sample_ids]  # Pass version to the submit script

    # Print the command being executed for debugging
    echo_message(
        f"executing command: {' '.join(cmd)}",
        "action",
    )

    # Execute the command for all valid samples
    echo_message(
        f"starting starsolo for samples: {sample_ids}...",
        "progress",
    )
    try:
        result = subprocess.run(
            cmd,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        echo_message(
            f"starsolo submitted successfully:\n{result.stdout}",
            "progress",
        )
    except subprocess.CalledProcessError as e:
        # Log the stderr and return code
        echo_message(
            f"Error during starsolo execution: {e.stderr}",
            "warn",
        )

    echo_message(
        f"starsolo submission complete. run `bjobs -w`  for progress.",
        "success",
    )


if __name__ == "__main__":
    cmd()
