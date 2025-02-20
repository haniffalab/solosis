import os
import subprocess
import tempfile

import click
import pandas as pd

from solosis.utils.logging_utils import secho


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
    default="2.0.2",  # Set a default version for Cell Ranger ARC
    help="Cell Ranger ARC version to use (e.g., '2.0.2')",
)
@click.pass_context
def cmd(ctx, libraries, librariesfile, create_bam, version):
    """
    Cell Ranger ARC aligns GEX & ATAC seq reads... \n
    --------------------------------- \n
    Cell Ranger ARC (2.0.2) Software suite designed for analysing & interpreting scRNA seq data, including multi-omics data.
    """
    secho(
        f"Starting Process: {click.style(ctx.command.name, bold=True, underline=True)}",
        "info",
    )

    secho(f"loading Cell Ranger ARC Count version {version}")

    libraries_paths = []

    # Collect libraries file paths from the provided options
    if libraries:
        libraries_paths.append(libraries)

    if librariesfile:
        try:
            with open(librariesfile, "r") as f:
                libraries_paths.extend([line.strip() for line in f if line.strip()])
        except Exception as e:
            secho(
                f"Error reading libraries file: {e}",
                "error",
            )
            return

    if not libraries_paths:
        secho(
            f"No libraries provided. Use --libraries or --librariesfile",
            "error",
        )
        return

    # A list of valid libraries (with ID), where the path and contents has been validated.
    valid_libraries = []

    for lib_path in libraries_paths:
        if not os.path.exists(lib_path):
            secho(
                f"Libraries file {lib_path} does not exist. Skipping this file",
                "warn",
            )
            continue

        try:
            df = pd.read_csv(lib_path)
            required_columns = {"fastqs", "sample", "library_type"}

            if not required_columns.issubset(df.columns):
                secho(
                    f"Libraries file {lib_path} is missing required columns: {', '.join(required_columns - set(df.columns))}",
                    "error",
                )
                continue

            if not all(
                df["library_type"].isin(["Chromatin Accessibility", "Gene Expression"])
            ):
                secho(
                    f"Libraries file {lib_path} contains invalid 'library_type' values. Must be 'Chromatin Accessibility' or 'Gene Expression'",
                    "error",
                )
                continue

            # Generate ID (name of output directory) by concatenating sorted 'sample' values
            sorted_samples = sorted(df["sample"].dropna().astype(str).tolist())
            library_id = "_".join(sorted_samples)

            # Append the validated details
            valid_libraries.append((lib_path, library_id))
        except Exception as e:
            secho(
                f"Error validating libraries file {lib_path}: {e}",
                "error",
            )

    if not valid_libraries:
        secho(
            f"No valid libraries files found. Exiting",
            "error",
        )
        return

    # Get the data directory from the environment variable
    team_data_dir = os.getenv("TEAM_DATA_DIR")
    if not team_data_dir:
        secho(
            f"TEAM_DATA_DIR environment variable is not set",
            "error",
        )
        return

    # Create a temporary file to store library paths and IDs
    tmp_dir = os.path.join(team_data_dir, "tmp")
    with tempfile.NamedTemporaryFile(
        mode="w", delete=False, suffix=".txt", dir=tmp_dir
    ) as temp_file:
        for lib_path, library_id in valid_libraries:
            temp_file.write(f"{lib_path},{library_id}\n")
        temp_file_path = temp_file.name

    script_dir = os.path.dirname(os.path.abspath(__file__))
    cellranger_submit_script = os.path.abspath(
        os.path.join(script_dir, "../../../bin/alignment/cellranger-arc/submit.sh")
    )

    cmd = [
        cellranger_submit_script,
        temp_file_path,
        version,
    ]
    if not create_bam:
        cmd.append("--no-bam")

    secho(
        f"Executing command: {' '.join(cmd)}",
        "action",
    )

    secho(
        f"Starting Cell Ranger ARC for libraries listed in: {temp_file_path}...",
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
        secho(
            f"Cell Ranger ARC submitted successfully:\n{result.stdout}",
            "progress",
        )
    except subprocess.CalledProcessError as e:
        secho(
            f"Error during Cell Ranger ARC execution: {e.stderr}",
            "warn",
        )

    secho(
        f"Cell Ranger ARC submission complete. Run `bjobs -w` for progress.",
        "success",
    )


if __name__ == "__main__":
    cmd()
