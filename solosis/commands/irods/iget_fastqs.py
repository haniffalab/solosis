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
def cmd(sample, samplefile):
    """Downloads fastqs from iRODS."""
    ctx = click.get_current_context()
    secho(
        f"Starting Process: {click.style(ctx.command.name, bold=True, underline=True)}",
        "info",
    )

    irods_auth()

    samples = collect_samples(sample, samplefile)

    samples_to_download = []
    for sample in samples:
        fastq_path = os.path.join(os.getenv("TEAM_SAMPLES_DIR"), sample, "fastq")
        if os.path.exists(fastq_path) and any(
            f.endswith(ext) for ext in FASTQ_EXTENSIONS for f in os.listdir(fastq_path)
        ):
            secho(
                f"FASTQ files already found for sample '{sample}' in {fastq_path}. Skipping download.",
                "warn",
            )
        else:
            samples_to_download.append(sample)

    if not samples_to_download:
        secho(
            f"All samples already proccessed.",
            "warn",
        )
        return

    with tempfile.NamedTemporaryFile(
        delete=False, mode="w", suffix=".txt", dir=os.environ["TEAM_TMP_DIR"]
    ) as tmpfile:
        secho(f"Temporary command file created: {tmpfile.name}", "info")
        os.chmod(tmpfile.name, 0o660)
        for sample in samples_to_download:
            tmpfile.write(sample + "\n")

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
                tmpfile.name,
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
