import os
import subprocess
import sys

import click
import pandas as pd

from solosis.utils import echo_message, log_command

FASTQ_EXTENSIONS = [".fastq", ".fastq.gz"]


@click.command("cellranger-count")
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
    Cell Ranger  aligns and analyses sc-RNA seq data...\n
    --------------------------------- \n
    Cell Ranger (7.2.0) performs sample demultiplexing, barcode processing,
    and gene counting for single-cell 3' and 5' RNA-seq data, as well as
    V(D)J transcript sequence assembly.
    """
    log_command(ctx)
    echo_message(
        f"Starting Process: {click.style(ctx.command.name, bold=True, underline=True)}",
        "info",
    )

    echo_message(f"loading Cell Ranger Count version {version}")

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
        existing_path = os.path.join(samples_dir, sample, "cellranger", version)
        # Check if cellranger output already exists in the directory
        if os.path.exists(existing_path):
            echo_message(
                f"cellranger-count output(s) already exist for sample {sample} in {existing_path}. Skipping this sample",
                "warn",
            )
        else:
            valid_samples.append(sample)

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
    cellranger_submit_script = os.path.abspath(
        os.path.join(script_dir, "../../../bin/alignment/cellranger-count/submit.sh")
    )

    # Construct the command with optional BAM flag
    cmd = [
        cellranger_submit_script,
        sample_ids,
        version,
    ]  # Pass version to the submit script
    if not create_bam:
        cmd.append("--no-bam")

    # Print the command being executed for debugging
    echo_message(
        f"executing command: {' '.join(cmd)}",
        "action",
    )

    # Execute the command for all valid samples
    echo_message(
        f"starting Cell Ranger for samples: {sample_ids}...",
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
            f"Cell Ranger submitted successfully:\n{result.stdout}",
            "progress",
        )
    except subprocess.CalledProcessError as e:
        # Log the stderr and return code
        echo_message(
            f"Error during Cell Ranger execution: {e.stderr}",
            "warn",
        )

    echo_message(
        f"cellranger submission complete. run `bjobs -w`  for progress.",
        "success",
    )


if __name__ == "__main__":
    cmd()
