import os
import subprocess

import click
import pandas as pd

FASTQ_EXTENSIONS = [".fastq", ".fastq.gz"]


@click.command("pull-fastqs")
@click.option("--sample", type=str, help="Sample ID (string)")
@click.option(
    "--samplefile",
    type=click.Path(exists=True),
    help="Path to a CSV or TSV file containing sample IDs",
)
def cmd(sample, samplefile):
    """
    Downloading fastqs from iRODS...

    Utilising NF-irods-to-fastq pipeline developed by Cellgeni.
    Pulled directly from Github repo- up-to-date.
    """
    print("Using iRODS to download data")
    print("If you have a large set of files, this command will take a while to run")

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
    team_sample_data_dir = os.getenv(
        "team_sample_data_dir", "/lustre/scratch126/cellgen/team298/data/samples"
    )

    if not os.path.isdir(team_sample_data_dir):
        click.echo(
            f"Error: The temporary data directory '{team_sample_data_dir}' does not exist."
        )
        return

    # Check each sample
    samples_to_download = []
    for sample in samples:
        # Path where FASTQ files are expected for each sample
        fastq_path = os.path.join(team_sample_data_dir, sample, "fastq")

        # Check if FASTQ files exist in the directory for the sample
        if os.path.exists(fastq_path) and any(
            f.endswith(ext) for ext in FASTQ_EXTENSIONS for f in os.listdir(fastq_path)
        ):
            click.echo(
                f"Warning: FASTQ files already found for sample '{sample}' in {fastq_path}. Skipping download."
            )
        else:
            samples_to_download.append(sample)

    # Inform if there are samples that need FASTQ downloads
    if samples_to_download:
        click.echo(f"Samples without FASTQ files: {samples_to_download}")
    else:
        click.echo(
            "All provided samples already have FASTQ files. No downloads required."
        )
        return  # Exit if no samples need downloading

    # Join all sample to download IDs into a single string, separated by commas
    sample_ids = ",".join(samples_to_download)

    # Path to the script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    irods_to_fastq_script = os.path.abspath(
        os.path.join(script_dir, "../../../bin/irods/pull-fastqs/submit.sh")
    )

    # Construct the command with optional BAM flag
    cmd = [
        irods_to_fastq_script,
        sample_ids,
    ]

    # Print the command being executed for debugging
    click.echo(f"Executing command: {' '.join(cmd)}")

    # Execute the command for all valid samples
    click.echo(f"Starting pull-fastq for samples: {sample_ids}...")
    try:
        with subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        ) as process:
            stderr = process.communicate()[1]
            if process.returncode != 0:
                click.echo(f"Error during pull-fastq execution: {stderr}")
            else:
                click.echo("pull-fastq completed successfully.")
    except subprocess.CalledProcessError as e:
        # Log the stderr and return code
        click.echo(f"Error during pull-fastq execution: {e.stderr}")

    click.echo("pull-fastq processing complete")


if __name__ == "__main__":
    cmd()
