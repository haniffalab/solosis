import os
import subprocess
import sys

import click
import pandas as pd

from solosis.utils import echo_message, log_command


@click.command("cellranger-arc")
@click.option(
    "--libraries", type=click.Path(exists=True), help="Path to a single libraries file"
)
@click.option(
    "--librariesfile",
    type=click.Path(exists=True),
    help="Path to a CSV containing paths to multiple library files",
)
@click.option(
    "--create-bam",
    is_flag=True,
    default=False,
    help="Generate BAM files for each library",
)
@click.option(
    "--version",
    type=str,
    default="2.1.0",  # Set a default version for Cell Ranger ARC
    help="Cell Ranger ARC version to use (e.g., '2.1.0')",
)
@click.pass_context
def cmd(ctx, libraries, librariesfile, create_bam, version):
    """
    Run Cell Ranger ARC for multi-omics (ATAC + Gene Expression) analysis.

    Cell Ranger ARC (2.1.0) performs sample demultiplexing, barcode processing,
    and multi-modal data analysis for single-cell ATAC and gene expression data.
    """
    log_command(ctx)
    echo_message(
        f"Starting Process: {click.style(ctx.command.name, bold=True, underline=True)}",
        "info",
    )
    echo_message(f"loading Cell Ranger ARC Count version {version}")

    libraries_paths = []

    # Collect libraries file paths from the provided options
    if libraries:
        libraries_paths.append(libraries)

    if librariesfile:
        try:
            with open(librariesfile, "r") as f:
                libraries_paths.extend([line.strip() for line in f if line.strip()])
        except Exception as e:
            echo_message(
                f"Error reading libraries file: {e}",
                "error",
            )
            return

    if not libraries_paths:
        echo_message(
            f"No libraries provided. Use --libraries or --librariesfile",
            "error",
        )
        return

    valid_libraries = []

    for lib_path in libraries_paths:
        if not os.path.exists(lib_path):
            echo_message(
                f"Libraries file {lib_path} does not exist. Skipping this file",
                "warn",
            )
            continue

        try:
            df = pd.read_csv(lib_path)
            required_columns = {"fastqs", "sample", "library_type"}

            if not required_columns.issubset(df.columns):
                echo_message(
                    f"Libraries file {lib_path} is missing required columns: {', '.join(required_columns - set(df.columns))}",
                    "error",
                )
                continue

            if not all(
                df["library_type"].isin(["Chromatin Accessibility", "Gene Expression"])
            ):
                echo_message(
                    f"Libraries file {lib_path} contains invalid 'library_type' values. Must be 'Chromatin Accessibility' or 'Gene Expression'",
                    "error",
                )
                continue

            valid_libraries.append(lib_path)
        except Exception as e:
            echo_message(
                f"Error validating libraries file {lib_path}: {e}",
                "error",
            )

    if not valid_libraries:
        echo_message(
            f"No valid libraries files found. Exiting",
            "error",
        )
        return

    libraries_arg = ",".join(valid_libraries)

    script_dir = os.path.dirname(os.path.abspath(__file__))
    cellranger_submit_script = os.path.abspath(
        os.path.join(script_dir, "../../../bin/alignment/cellranger-arc/submit.sh")
    )

    cmd = [
        cellranger_submit_script,
        libraries_arg,
        version,
    ]
    if not create_bam:
        cmd.append("--no-bam")

    echo_message(
        f"Executing command: {' '.join(cmd)}",
        "action",
    )

    echo_message(
        f"Starting Cell Ranger ARC for libraries: {libraries_arg}...",
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
            f"Cell Ranger ARC submitted successfully:\n{result.stdout}",
            "progress",
        )
    except subprocess.CalledProcessError as e:
        echo_message(
            f"Error during Cell Ranger ARC execution: {e.stderr}",
            "warn",
        )

    echo_message(
        f"Cell Ranger ARC submission complete. Run `bjobs -w` for progress.",
        "success",
    )


if __name__ == "__main__":
    cmd()
