import os
import subprocess
import sys
import time

import click
import pandas as pd

FASTQ_EXTENSIONS = [".fastq", ".fastq.gz"]  # remove?

from solosis.utils import echo_message


def spinner():
    """Generator for spinner animation in the terminal."""
    spinner_frames = ["|", "/", "-", "\\"]
    while True:
        for frame in spinner_frames:
            yield frame


# change to pull-cellranger
@click.command("pull-processed")
@click.option("--sample", type=str, help="Sample ID (string)")
@click.option(
    "--samplefile",
    type=click.Path(exists=True),
    help="Path to a CSV or TSV file containing sample IDs",
)
@click.option(
    "--retainbam",
    default=False,
    is_flag=True,
    required=False,
    help="Download alignment bam file",
)
@click.option(
    "--overwrite",
    default=False,
    is_flag=True,
    required=False,
    help="Overwrite existing folder contents",
)
def cmd(sample, samplefile, retainbam, overwrite):
    """
    Downloading cellranger output(s) from iRODS..

    [insert additional text here]

    """

    echo_message(
        f"using iRODS to download data",
        "info",
    )
    echo_message(
        f"if you have a large set of files, this command will take a while to run",
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
        echo_message(
            f"try using solosis-cli pull-cellranger --help",
            "warn",
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

    # Check each sample
    samples_to_download = []
    for sample in samples:
        # Path where cellranger outputs are expected for each sample
        cellranger_path = os.path.join(
            team_sample_data_dir, sample, "sanger-cellranger"
        )

        # Check if FASTQ files exist in the directory for the sample
        if os.path.exists(cellranger_path):
            echo_message(
                f"Cellranger outputs already downloaded for sample '{sample}' in {cellranger_path}. Skipping download.",
                "warn",
            )
        else:
            samples_to_download.append(sample)

    # Inform if there are samples that need FASTQ downloads
    if samples_to_download:
        echo_message(
            f"samples for cellranger output download: {samples_to_download}",
            "progress",
        )
    else:
        echo_message(
            f"all provided samples already have sanger processed cellranger outputs. No downloads required.",
            "warn",
        )
        return  # Exit if no samples need downloading

    # Join all sample to download IDs into a single string, separated by commas
    sample_ids = ",".join(samples_to_download)

    # Path to the script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    pull_cellranger_script = os.path.abspath(
        os.path.join(script_dir, "../../../bin/irods/pull-cellranger/submit.sh")
    )

    # Construct the command with optional BAM flag
    cmd = [
        pull_cellranger_script,
        sample_ids,
    ]

    # Print the command being executed for debugging
    echo_message(
        f"executing command: {' '.join(cmd)}",
        "progress",
    )

    # Create the spinner generator
    spin = spinner()

    # Execute the command with an active spinner

    echo_message(
        f"starting process for samples: {sample_ids}...",
        "progress",
    )
    try:
        with subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        ) as process:
            # While the command runs, show the spinner animation
            while True:
                # Check if the process has finished
                retcode = process.poll()
                if retcode is not None:  # Process has finished
                    break
                sys.stdout.write("\r" + next(spin))  # Overwrite the spinner
                sys.stdout.flush()  # Force output to the terminal
                time.sleep(0.1)  # Delay between spinner updates

            # Capture the output
            stdout, stderr = process.communicate()
            if process.returncode != 0:
                echo_message(
                    f"error during execution: {stderr}",
                    "warn",
                )
            else:
                echo_message(
                    f"LSF job submitted successfully:\n{stdout}",
                    "success",
                )
                echo_message(
                    f"use `bjobs` to monitor job completion. view logs at $HOME/logs",
                    "info",
                )
                echo_message(
                    f"view job success at $HOME/logs",
                    "info",
                )
    except subprocess.CalledProcessError as e:
        # Log the stderr and return code
        echo_message(
            f"error during execution: {e.stderr}",
            "warn",
        )

    # echo_message(
    #    f"processing complete",
    #    "success",
    # )


if __name__ == "__main__":
    cmd()
