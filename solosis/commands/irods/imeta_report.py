import logging
import os

import click
import pandas as pd
from tabulate import tabulate

from solosis.utils.env_utils import irods_auth
from solosis.utils.input_utils import collect_samples
from solosis.utils.logging_utils import debug, log
from solosis.utils.state import logger
from solosis.utils.subprocess_utils import popen


@click.command("imeta-report")
@click.option("--sample", type=str, help="Sample ID (string).")
@click.option(
    "--samplefile",
    type=click.Path(exists=True),
    help="Path to a CSV or TSV file containing sample IDs.",
)
@debug
@log
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

    summary_data = []
    all_data = []

    for sample in samples:
        logger.info(f"Processing sample: {sample}")

        sample_dir = os.path.join(os.getenv("TEAM_SAMPLES_DIR"), sample)
        os.makedirs(sample_dir, exist_ok=True)
        report_path = os.path.join(sample_dir, "imeta_report.csv")

        imeta_report_script = os.path.abspath(
            os.path.join(
                os.getenv("SCRIPT_BIN"),
                "irods/imeta_report.sh",
            )
        )
        popen([imeta_report_script, sample, report_path])
        if os.path.exists(report_path):
            df = pd.read_csv(
                report_path, header=None, names=["collection_type", "path"]
            )
            crams = len(df[df["collection_type"] == "CRAM"])
            collections = len(df[df["collection_type"] == "COLLECTION"])
            summary_data.append([sample, crams, collections])

            # Concatendate reports
            df.insert(0, "sample", sample)
            all_data.append(df)

    # Display summary table for samples
    headers = [
        "Sample",
        "CRAM",
        "COLLECTION",
    ]
    table = tabulate(
        summary_data, headers, tablefmt="pretty", numalign="left", stralign="left"
    )
    logger.info(f"Summary table... \n{table}")

    # Output combined report for samples
    execution_dir = os.getcwd()
    all_report_path = os.path.join(execution_dir, "all-imeta-report.csv")

    if all_data:
        all_df = pd.concat(all_data, ignore_index=True)
        all_df.to_csv(all_report_path, index=False)
        logger.info(f"Report generated: {all_report_path}")
    else:
        logger.warning("No data to show.")


if __name__ == "__main__":
    cmd()
