import logging
import os
import tempfile

import click
import pandas as pd

from solosis.utils.logging_utils import debug
from solosis.utils.lsf_utils import lsf_options_std, submit_lsf_job_array
from solosis.utils.state import logger


@lsf_options_std
@debug
@click.command("cellranger-arc-count")
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
    default="2.0.2",
    help="Cell Ranger ARC version to use (e.g., '2.0.2')",
)
def cmd(libraries, librariesfile, create_bam, version, mem, cpu, queue, debug):
    """Single-cell multiomic data processing"""
    if debug:
        logger.setLevel(logging.DEBUG)

    ctx = click.get_current_context()
    logger.debug(
        f"Starting command: {click.style(ctx.command.name, bold=True, underline=True)}"
    )
    logger.debug(f"Loading Cell Ranger ARC Count version {version}")

    libraries_paths = []

    if libraries:
        libraries_paths.append(libraries)

    if librariesfile:
        try:
            with open(librariesfile, "r") as f:
                libraries_paths.extend([line.strip() for line in f if line.strip()])
        except Exception as e:
            logger.error(f"Error reading libraries file: {e}")
            return

    if not libraries_paths:
        logger.error(f"No libraries provided. Use --libraries or --librariesfile")
        raise click.Abort()

    # A list of valid libraries (with ID), where the path and contents has been validated.
    valid_libraries = []
    for library_path in libraries_paths:
        if not os.path.exists(library_path):
            logger.warning(
                f"Libraries file {library_path} does not exist. Skipping this file"
            )
            continue

        try:
            df = pd.read_csv(library_path)
            required_columns = {"fastqs", "sample", "library_type"}

            if not required_columns.issubset(df.columns):
                logger.warning(
                    f"Libraries file {library_path} is missing required columns: {', '.join(required_columns - set(df.columns))}"
                )
                continue

            if not all(
                df["library_type"].isin(["Chromatin Accessibility", "Gene Expression"])
            ):
                logger.warning(
                    f"Libraries file {library_path} contains invalid 'library_type' values. Must be 'Chromatin Accessibility' or 'Gene Expression'"
                )
                continue

            # Generate ID (name of output directory) by concatenating sorted 'sample' values
            sorted_samples = sorted(df["sample"].dropna().astype(str).tolist())
            library_id = "_".join(sorted_samples)
            output_dir = os.path.join(
                os.getenv("TEAM_SAMPLES_DIR"), "cellranger_arc", library_id
            )

            # Append the validated details
            valid_libraries.append(
                {
                    "id": library_id,
                    "output_dir": output_dir,
                    "libraries_path": library_path,
                }
            )
        except Exception as e:
            logger.error(f"Error validating libraries file {library_path}: {e}")

    if not valid_libraries:
        logger.error(f"No valid libraries files found. Exiting")
        raise click.Abort()

    cellranger_arc_count_path = os.path.abspath(
        os.path.join(
            os.getenv("SCRIPT_BIN"),
            "cellranger/cellranger_arc_count.sh",
        )
    )

    with tempfile.NamedTemporaryFile(
        delete=False, mode="w", suffix=".txt", dir=os.environ["TEAM_TMP_DIR"]
    ) as tmpfile:
        logger.info(f"Temporary command file created: {tmpfile.name}")
        os.chmod(tmpfile.name, 0o660)
        for library in valid_libraries:
            command = f"{cellranger_arc_count_path} {library['id']} {library['output_dir']} {library['libraries_path']} {version} {cpu} {mem}"
            tmpfile.write(command + "\n")

    submit_lsf_job_array(
        command_file=tmpfile.name,
        job_name="cellranger_arc_count_job_array",
        cpu=cpu,
        mem=mem,
        queue=queue,
    )


if __name__ == "__main__":
    cmd()
