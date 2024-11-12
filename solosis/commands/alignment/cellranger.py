import os
import subprocess

import click
import pandas as pd

from solosis.utils import echo_message

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
    # Print a clear introductory message
    echo_message(
        f"launching: {click.style('cellranger', bold=True, underline=True)}",
        "info",
    )
    echo_message(f"loading Cell Ranger version {version}")

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
                    click.style(
                        "Error: Unsupported file format. Please provide a .csv or .tsv file",
                        fg="red",
                        bold=True,
                    )
                )
                return

            df = pd.read_csv(samplefile, sep=sep)

            if "sample_id" in df.columns:
                samples.extend(df["sample_id"].dropna().astype(str).tolist())
            else:
                click.echo(
                    click.style(
                        'Error: File must contain a "sample_id" column',
                        fg="red",
                        bold=True,
                    )
                )
                return
        except Exception as e:
            click.echo(
                click.style(f"Error reading sample file: {e}", fg="red", bold=True)
            )
            return

    if not samples:
        click.echo(
            click.style(
                "Error: No samples provided. Use --sample or --samplefile",
                fg="red",
                bold=True,
            )
        )
        return

    # Define the FASTQ path and validate each sample
    team_sample_data_dir = os.getenv(
        "team_sample_data_dir", "/lustre/scratch126/cellgen/team298/data/samples"
    )

    if not os.path.isdir(team_sample_data_dir):
        echo_message(
            f"sample data directory '{team_sample_data_dir}' does not exist",
            "error",
        )
        return

    valid_samples = []
    for sample in samples:
        fastq_path = os.path.join(team_sample_data_dir, sample, "fastq")

        # Check if FASTQ files exist in the directory
        if os.path.exists(fastq_path) and any(
            f.endswith(ext) for ext in FASTQ_EXTENSIONS for f in os.listdir(fastq_path)
        ):
            valid_samples.append(sample)
        else:
            click.echo(
                click.style(
                    f"Warning: No FASTQ files found for sample {sample} in {fastq_path}. Skipping this sample",
                    fg="yellow",
                )
            )

    if not valid_samples:
        click.echo(
            click.style(
                "Error: No valid samples found with FASTQ files. Exiting",
                fg="red",
                bold=True,
            )
        )
        return

    # Join all valid sample IDs into a single string, separated by commas
    sample_ids = ",".join(valid_samples)

    # Path to the Cell Ranger submission script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    cellranger_submit_script = os.path.abspath(
        os.path.join(script_dir, "../../../bin/alignment/cellranger/submit.sh")
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
    click.echo(click.style(f"Executing command: {' '.join(cmd)}", fg="cyan"))

    # Execute the command for all valid samples
    click.echo(
        click.style(
            f"Starting Cell Ranger for samples: {sample_ids}...", fg="green", bold=True
        )
    )
    try:
        result = subprocess.run(
            cmd,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        click.echo(
            click.style(
                f"Cell Ranger completed successfully:\n{result.stdout}", fg="green"
            )
        )
    except subprocess.CalledProcessError as e:
        # Log the stderr and return code
        click.echo(
            click.style(
                f"Error during Cell Ranger execution: {e.stderr}", fg="red", bold=True
            )
        )

    click.echo(click.style("Cell Ranger processing complete", fg="green"))


if __name__ == "__main__":
    cmd()
