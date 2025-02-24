import os
import subprocess

import click
import pandas as pd
from tabulate import tabulate

from solosis.utils.env_utils import irods_auth
from solosis.utils.input_utils import collect_samples
from solosis.utils.logging_utils import secho


# change to pull-cellranger
@click.command("imeta-report")
@click.option("--sample", type=str, help="Sample ID (string).")
@click.option(
    "--samplefile",
    type=click.Path(exists=True),
    help="Path to a CSV or TSV file containing sample IDs.",
)
def cmd(sample, samplefile):
    """
    Generates report of data available on iRODS
    """
    ctx = click.get_current_context()
    secho(
        f"Starting Process: {click.style(ctx.command.name, bold=True, underline=True)}",
        "info",
    )

    irods_auth()

    samples = collect_samples(sample, samplefile)

    data = []

    # Iterate over the samples and run the subprocess for each sample
    for sample in samples:
        secho(f"Processing sample: {sample}", "info")

        # Create report directory for the sample
        sample_dir = os.path.join(os.getenv("TEAM_SAMPLES_DIR"), sample)
        os.makedirs(sample_dir, exist_ok=True)
        report_path = os.path.join(sample_dir, "imeta_report.csv")

        # Path to the script
        imeta_report_script = os.path.abspath(
            os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                "../../../bin/irods/imeta_report.sh",
            )
        )

        try:
            result = subprocess.run(
                [imeta_report_script, sample, report_path],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            # Print each line from stdout with the "info" prefix
            for line in result.stdout.splitlines():
                secho(f"{line}", "info")

            # Now read the report and process it
            if os.path.exists(report_path):
                # Load the report as a dataframe
                df = pd.read_csv(
                    report_path, header=None, names=["collection_type", "path"]
                )

                # Assuming the report has 'Cram' and 'Cell Ranger' columns for the data
                # Create a summary table
                crams = len(df[df["collection_type"] == "CRAM"])
                cellranger = len(df[df["collection_type"] == "CellRanger"])

                # Add summary to a final table
                data.append([sample, crams, cellranger])

        except subprocess.CalledProcessError as e:
            # Catch subprocess-specific errors (e.g., command failed with non-zero exit code)
            secho(f"Command '{e.cmd}' failed with return code {e.returncode}", "error")
            secho(f"Standard Error: {e.stderr}", "error")
            secho(f"Standard Output: {e.stdout}", "info")
        except Exception as e:
            # Catch any unexpected errors
            secho(f"Unexpected error: {str(e)}", "error")

        headers = [
            "Sample",
            "CRAM",
            "CellRanger",
        ]
        table = tabulate(
            data, headers, tablefmt="pretty", numalign="left", stralign="left"
        )
        secho(f"Summary table... \n{table}")


if __name__ == "__main__":
    cmd()
