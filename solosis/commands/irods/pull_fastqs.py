import os
import subprocess
import time

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
    click.echo("Using iRODS to download data")
    click.echo(
        "If you have a large set of files, this command will take a while to run"
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
        "TEAM_TMP_DATA_DIR", "/lustre/scratch126/cellgen/team298/data/samples"
    )

    if not os.path.isdir(team_tmp_data_dir):
        click.echo(
            f"Error: The temporary data directory '{team_tmp_data_dir}' does not exist."
        )
        return

    # Check each sample
    samples_to_download = []
    for sample in samples:
        fastq_path = os.path.join(team_tmp_data_dir, "fastq")

        # Check if FASTQ files are already in the directory
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

    # Join all sample IDs into a single string, separated by commas
    sample_ids = ",".join(samples_to_download)

    # Path to the Cell Ranger submission script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    pullfastq_submit_script = os.path.abspath(
        os.path.join(script_dir, "../../../bin/irods/pull-fastqs/submit.sh")
    )

    # Construct the command with optional BAM flag
    cmd = [
        pullfastq_submit_script,
        sample_ids,
    ]

    # Print the command being executed for debugging
    click.echo(f"Executing command: {' '.join(cmd)}")

    # Define simulated pipeline stages for progress bar
    pipeline_stages = [
        "findCrams",
        "getMetadata",
        "parseMetadata",
        "combineMetadata",
        "downloadCram",
        "cramToFastq",
        "calculateReadLength",
        "renameATAC",
        "saveMetaToJson",
        "updateMetadata",
    ]

    # Start subprocess for Nextflow
    try:
        with subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        ) as process:
            label_text = "Running Nextflow Pipeline..."
            with click.progressbar(pipeline_stages, label=label_text) as stages:
                for stage in stages:
                    # Read and print Nextflow output if available
                    output = process.stdout.readline()
                    if output:
                        print(output.strip())  # Print output line-by-line
                    time.sleep(1)  # Simulate processing time per stage

                    # Check if Nextflow pipeline has finished
                    if process.poll() is not None:
                        break

            # Capture any remaining stdout and stderr
            stdout, stderr = process.communicate()
            if process.returncode != 0:
                click.echo(f"Error during pull-fastq execution: {stderr}")
            else:
                click.echo("pull-fastq completed successfully.")
    except subprocess.CalledProcessError as e:
        click.echo(f"Error during pull-fastq execution: {e.stderr}")

    click.echo("pull-fastq processing complete")


if __name__ == "__main__":
    cmd()
