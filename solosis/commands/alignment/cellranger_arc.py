import os
import subprocess

import click
import pandas as pd

from solosis.utils import echo_lsf_submission_message, echo_message

FASTQ_EXTENSIONS = [".fastq", ".fastq.gz"]


@click.command("cellranger-arc")
@click.option("--sample", type=str, help="Sample ID (string)")
@click.option(
    "--samplefile",
    type=click.Path(exists=True),
    help="Path to a CSV or TSV file containing sample IDs",
)
@click.option(
    "--libraries",
    type=click.Path(exists=True),
    help="Path to a CSV file containing libraries. columns needed (fastqs|sample|library_type). library types (Chromatin Accessibility|Gene Expression).",
)
@click.option(
    "--version",
    type=str,
    default="2.0.2",  # Set a default version
    help="Cellranger-arc version to use (e.g., '2.0.2')",
)
# @click.option("--includebam", is_flag=True, default=False, help="Include BAM files",)
def cmd(sample, samplefile, libraries, version):  ##will need to add 'includebam'
    """
    cellranger-arc aligns GEX & ATAC seq reads... \n
    --------------------------------- \n
    cellranger-arc (2.0.2) Software suite designed for analysing & interpreting scRNA seq & Multiome data, including multi-omics data.

    """
    ctx = click.get_current_context()
    echo_message(
        f"Starting Process: {click.style(ctx.command.name, bold=True, underline=True)}",
        "info",
    )
    echo_message(f"loading cellranger-arc version {version}")

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
                    f"unsupported file format. please provide a .csv or .tsv file",
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
            f"no samples provided. Use `--sample` or `--samplefile`",
            "error",
        )
        return

    ############################################
    # Read libraries from a file if provided
    if libraries:
        try:
            sep = "," if libraries.endswith(".csv") else None
            if sep is None:
                echo_message(
                    f"unsupported file format. please provide a .csv file",
                    "error",
                )
                return

            df = pd.read_csv(libraries, sep=sep)

            column_names = {"fastqs", "sample", "library_type"}

            if column_names.issubset(df.columns):
                # Extend the libraries list with data from required columns
                libraries.extend(
                    df["fastqs"].dropna().astype(str).tolist()
                    + df["sample"].dropna().astype(str).tolist()
                    + df["library_type"].dropna().astype(str).tolist()
                )
            else:
                # Identify missing columns
                missing_columns = column_names - set(df.columns)
                echo_message(
                    f"file must contain the following missing columns: {', '.join(missing_columns)}",
                    "error",
                )
                return

            if "sample" in df.columns:
                libraries.extend(df["sample"].dropna().astype(str).tolist())
            else:
                echo_message(
                    f"file must contain a 'sample' column",
                    "error",
                )
                return
            if "library_type" in df.columns:
                libraries.extend(df["library_type"].dropna().astype(str).tolist())
            else:
                echo_message(
                    f"file must contain a 'library_type' column",
                    "error",
                )
                return
        except Exception as e:
            echo_message(
                f"error reading libraries file: {e}",
                "error",
            )
            return

    if not libraries:
        echo_message(
            f"no libraries provided. Use `--libraries`",
            "error",
        )
        return
    ############################################

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

    ###########
    # INSERT LOGIC FOR EXISTENCE OF LIBRARIES.CSV
    ###########

    # Join all valid sample IDs into a single string, separated by commas
    sample_ids = ",".join(valid_samples)

    # Path to the Cellranger-arc submission script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    cellranger_arc_submit_script = os.path.abspath(
        os.path.join(script_dir, "../../../bin/alignment/cellranger-arc/submit.sh")
    )

    # Construct the command with optional BAM flag
    cmd = [
        cellranger_arc_submit_script,
        sample_ids,
        libraries,
        version,
    ]  # Pass version to the submit script

    # Print the command being executed for debugging
    echo_message(
        f"executing command: {' '.join(cmd)}",
        "action",
    )

    # Execute the command for all valid samples
    echo_message(
        f"starting cellranger-arc for samples: {sample_ids}...",
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
            f"cellranger-arc submitted successfully:\n{result.stdout}",
            "progress",
        )
    except subprocess.CalledProcessError as e:
        # Log the stderr and return code
        echo_message(
            f"Error during cellranger-arc execution: {e.stderr}",
            "warn",
        )

    echo_message(
        f"cellranger-arc submission complete. run `bjobs -w`  for progress.",
        "success",
    )


if __name__ == "__main__":
    cmd()
