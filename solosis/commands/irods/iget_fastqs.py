import os
import subprocess
import tempfile
from datetime import datetime

import click

from solosis.utils.env_utils import irods_auth
from solosis.utils.input_utils import collect_samples
from solosis.utils.logging_utils import secho

FASTQ_EXTENSIONS = [".fastq", ".fastq.gz"]


@click.command("iget-fastqs")
@click.option("--sample", type=str, help="Sample ID (string)")
@click.option(
    "--samplefile",
    type=click.Path(exists=True),
    help="Path to a CSV or TSV file containing sample IDs",
)
@click.pass_context
def cmd(ctx, sample, samplefile):
    """Downloads fastqs from iRODS."""
    secho(
        f"Starting Process: {click.style(ctx.command.name, bold=True, underline=True)}",
        "info",
    )

    irods_auth()

    samples = collect_samples(sample, samplefile)

    # Check each sample
    samples_to_download = []
    for sample in samples:
        # Path where FASTQ files are expected for each sample
        fastq_path = os.path.join(os.getenv("TEAM_SAMPLES_DIR"), sample, "fastq")

        # Check if FASTQ files exist in the directory for the sample
        if os.path.exists(fastq_path) and any(
            f.endswith(ext) for ext in FASTQ_EXTENSIONS for f in os.listdir(fastq_path)
        ):
            secho(
                f"FASTQ files already found for sample '{sample}' in {fastq_path}. Skipping download.",
                "warn",
            )
        else:
            samples_to_download.append(sample)

    # Inform if there are samples that need FASTQ downloads
    if not samples_to_download:
        secho(
            f"All samples already proccessed.",
            "warn",
        )
        return

    # Define the directory where you want to create the temp file
    temp_dir = os.path.join(os.environ.get("TEAM_DATA_DIR"), "tmp")
    os.makedirs(temp_dir, exist_ok=True)

    # Create a temporary file to hold the sample IDs
    with tempfile.NamedTemporaryFile(
        delete=False, mode="w", suffix=".txt", dir=temp_dir
    ) as tmpfile:
        for sample in samples_to_download:
            tmpfile.write(sample + "\n")
        tmpfile_path = tmpfile.name
        os.chmod(tmpfile_path, 0o660)

    # Path to the script
    irods_to_fastq_script = os.path.abspath(
        os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "../../../bin/irods/nf-irods-to-fastq.sh",
        )
    )

    try:
        process = subprocess.Popen(
            [
                irods_to_fastq_script,
                tmpfile_path,
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        # Process stdout in real-time
        for line in process.stdout:
            timestamp = datetime.now().strftime("%H:%M:%S")
            secho(f"[{timestamp}] {line.strip()}", "progress")

        # Process stderr in real-time
        for line in process.stderr:
            timestamp = datetime.now().strftime("%H:%M:%S")
            secho(f"[{timestamp}] {line.strip()}", "warn")

        process.wait()
        if process.returncode != 0:
            secho(f"error during execution. Return code: {process.returncode}", "error")
        else:
            secho("process completed successfully.", "success")
    except Exception as e:
        secho(f"error executing command: {e}", "error")


if __name__ == "__main__":
    cmd()
