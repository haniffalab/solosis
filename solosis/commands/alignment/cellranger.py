import os
import subprocess

import click
import pandas as pd

FASTQ_EXTENSIONS = [".fastq", ".fastq.gz"]


@click.command("cellranger")
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
def cmd(sample, samplefile, create_bam, version):
    """
    Run Cell Ranger for single-cell RNA sequencing alignment and analysis

    Cell Ranger (7.2.0) performs sample demultiplexing, barcode processing,
    and gene counting for single-cell 3' and 5' RNA-seq data, as well as
    V(D)J transcript sequence assembly
    """
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
                click.echo(
                    "Error: Unsupported file format. Please provide a .csv or .tsv file"
                )
                return

            df = pd.read_csv(samplefile, sep=sep)

            if "sample_id" in df.columns:
                samples.extend(df["sample_id"].dropna().astype(str).tolist())
            else:
                click.echo('Error: File must contain a "sample_id" column')
                return
        except Exception as e:
            click.echo(f"Error reading sample file: {e}")
            return

    if not samples:
        click.echo("Error: No samples provided. Use --sample or --samplefile")
        return

    # Define the FASTQ path and validate each sample
    team_tmp_data_dir = os.getenv(
        "TEAM_TMP_DATA_DIR", "/lustre/scratch126/cellgen/team298/tmp"
    )

    if not os.path.isdir(team_tmp_data_dir):
        click.echo(
            f"Error: The temporary data directory '{team_tmp_data_dir}' does not exist."
        )
        return

    valid_samples = []
    for sample in samples:
        fastq_path = os.path.join(team_tmp_data_dir, sample)

        # Check if FASTQ files exist in the directory
        if os.path.exists(fastq_path) and any(
            f.endswith(ext) for ext in FASTQ_EXTENSIONS for f in os.listdir(fastq_path)
        ):
            valid_samples.append(sample)
        else:
            click.echo(
                f"Warning: No FASTQ files found for sample {sample} in {fastq_path}. Skipping this sample"
            )

    if not valid_samples:
        click.echo("Error: No valid samples found with FASTQ files. Exiting")
        return

    # Join all valid sample IDs into a single string, separated by commas
    sample_ids = ",".join(valid_samples)

    # Path to the Cell Ranger submission script
    cellranger_submit_script = os.path.abspath("./bin/alignment/cellranger/submit.sh")

    # Construct the command with optional BAM flag
    cmd = [
        cellranger_submit_script,
        sample_ids,
        version,
    ]  # Pass version to the submit script
    if not create_bam:
        cmd.append("--no-bam")

    # Print the command being executed for debugging
    click.echo(f"Executing command: {' '.join(cmd)}")

    # Execute the command for all valid samples
    click.echo(f"Starting Cell Ranger for samples: {sample_ids}...")
    try:
        result = subprocess.run(
            cmd,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        click.echo(f"Cell Ranger completed successfully:\n{result.stdout}")
    except subprocess.CalledProcessError as e:
        # Log the stderr and return code
        click.echo(f"Error during Cell Ranger execution: {e.stderr}")

    click.echo("Cell Ranger processing complete")


if __name__ == "__main__":
    cmd()
