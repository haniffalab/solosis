import logging
import os

import click
import pandas as pd
from tabulate import tabulate

from solosis.utils.env_utils import irods_auth
from solosis.utils.input_utils import collect_samples
from solosis.utils.logging_utils import debug
from solosis.utils.state import logger
from solosis.utils.subprocess_utils import popen


@debug
@click.command("imeta-report")
@click.option("--sample", type=str, help="Sample ID (string).")
@click.option(
    "--samplefile",
    type=click.Path(exists=True),
    help="Path to a CSV or TSV file containing sample IDs.",
)
def cmd(sample, samplefile, debug):
    """
    Generates report of data available on iRODS
    """
    if debug:
        logger.setLevel(logging.DEBUG)

    ctx = click.get_current_context()
    logger.debug(
        f"Starting command: {click.style(ctx.command.name, bold=True, underline=True)}"
    )

    if not irods_auth():
        raise click.Abort()

    samples = collect_samples(sample, samplefile)
    data = []
    for sample in samples:
        logger.info(f"Processing sample: {sample}")

        sample_dir = os.path.join(os.getenv("TEAM_SAMPLES_DIR"), sample)
        os.makedirs(sample_dir, exist_ok=True)
        report_path = os.path.join(sample_dir, "imeta_report.csv")

        imeta_report_script = os.path.abspath(
            os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                "../../../bin/irods/imeta_report.sh",
            )
        )
        popen([imeta_report_script, sample, report_path])
        if os.path.exists(report_path):
            df = pd.read_csv(
                report_path, header=None, names=["collection_type", "path"]
            )
            crams = len(df[df["collection_type"] == "CRAM"])
            cellranger = len(df[df["collection_type"] == "CellRanger"])
            data.append([sample, crams, cellranger])

        # Display summary table for individual samples
        headers = [
            "Sample",
            "CRAM",
            "CellRanger",
        ]
        table = tabulate(
            data, headers, tablefmt="pretty", numalign="left", stralign="left"
        )
        logger.info(f"Summary table... \n{table}")

    execution_dir = os.getcwd()
    all_report_path = os.path.join(execution_dir, "all-imeta-report.csv")
    all_data = []

    for sample in samples:
        report_path = os.path.join(
            os.getenv("TEAM_SAMPLES_DIR"), sample, "imeta_report.csv"
        )
        if os.path.exists(report_path):
            df = pd.read_csv(report_path, header=None, names=["file_type", "path"])
            df.insert(0, "sample", sample)  # Add the sample name as the first column
            all_data.append(df)

    # Combine all sample data into a single CSV report
    if all_data:
        combined_df = pd.concat(all_data, ignore_index=True)
        combined_df.to_csv(all_report_path, index=False)
        logger.info(f"Overall report generated: {all_report_path}")
    else:
        logger.warning("No reports found. 'all-imeta-report.csv' was not created.")


if __name__ == "__main__":
    cmd()
