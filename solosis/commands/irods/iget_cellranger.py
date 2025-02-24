import os
import subprocess

import click

from solosis.commands.irods.imeta_report import cmd as imeta_report
from solosis.utils.env_utils import irods_auth
from solosis.utils.input_utils import collect_samples
from solosis.utils.logging_utils import secho


# change to pull-cellranger
@click.command("iget-cellranger")
@click.option("--sample", type=str, help="Sample ID (string).")
@click.option(
    "--samplefile",
    type=click.Path(exists=True),
    help="Path to a CSV or TSV file containing sample IDs.",
)
def cmd(sample, samplefile):
    """Downloads cellranger outputs from iRODS."""
    ctx = click.get_current_context()
    secho(
        f"Starting Process: {click.style(ctx.command.name, bold=True, underline=True)}",
        "info",
    )

    irods_auth()

    samples = collect_samples(sample, samplefile)

    # Run imeta-report first and collect output
    secho("Running metadata report...", "info")
    report_results = ctx.invoke(imeta_report, sample=sample, samplefile=samplefile)
    secho(report_results)
    click.Abort()
    if not report_results:
        secho("No valid samples found from the report. Exiting.", "error")
        return

    # Check each sample
    samples_to_download = []
    for sample in samples:
        # Path where cellranger outputs are expected for each sample
        cellranger_path = os.path.join(
            os.getenv("TEAM_SAMPLES_DIR"), sample, "cellranger"
        )

    # Join all sample to download IDs into a single string, separated by commas
    sample_ids = ",".join(samples_to_download)

    # Path to the script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    pull_cellranger_script = os.path.abspath(
        os.path.join(script_dir, "../../../bin/irods/iget-cellranger/submit.sh")
    )

    # Construct the command with optional BAM flag
    cmd = [
        pull_cellranger_script,
        sample_ids,
    ]

    try:
        result = subprocess.run(
            cmd,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
    except subprocess.CalledProcessError as e:
        secho(
            f"Error during execution: {e.stderr}",
            "error",
        )


if __name__ == "__main__":
    cmd()
