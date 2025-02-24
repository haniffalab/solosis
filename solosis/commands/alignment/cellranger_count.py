import os
import subprocess
import tempfile

import click

from solosis.utils.input_utils import collect_samples
from solosis.utils.logging_utils import secho
from solosis.utils.lsf_utils import lsf_options, submit_lsf_job_array

FASTQ_EXTENSIONS = [".fastq", ".fastq.gz"]


@lsf_options
@click.command("cellranger-count")
@click.option("--sample", type=str, help="Sample ID (string)")
@click.option(
    "--samplefile",
    type=click.Path(exists=True),
    help="Path to a CSV or TSV file containing sample IDs",
)
@click.option(
    "--create-bam",
    is_flag=True,
    default=False,
    help="Generate BAM files for each sample",
)
@click.option(
    "--version",
    type=str,
    default="7.2.0",
    help="Cell Ranger version to use (e.g., '7.2.0')",
)
@click.pass_context
def cmd(ctx, sample, samplefile, create_bam, version, mem, cpu, queue):
    """scRNA-seq mapping and quantification"""
    secho(
        f"Starting Process: {click.style(ctx.command.name, bold=True, underline=True)}",
        "info",
    )
    secho(f"Using Cell Ranger version {version}", "info")

    samples = collect_samples(sample, samplefile)

    valid_samples = []
    for sample in samples:
        fastq_path = os.path.join(os.getenv("TEAM_SAMPLES_DIR"), sample, "fastq")
        if os.path.exists(fastq_path) and any(
            f.endswith(ext) for ext in FASTQ_EXTENSIONS for f in os.listdir(fastq_path)
        ):
            cellranger_path = os.path.join(
                os.getenv("TEAM_SAMPLES_DIR"), sample, "cellranger", version
            )
            if os.path.exists(cellranger_path):
                secho(
                    f"CellRanger output already exists for sample {sample} in {cellranger_path}. Skipping this sample",
                    "warn",
                )
            else:
                valid_samples.append(sample)
        else:
            secho(
                f"No FASTQ files found for sample {sample} in {fastq_path}. Skipping this sample",
                "warn",
            )

    if not valid_samples:
        secho(
            f"No valid samples found with FASTQ files. Exiting",
            "error",
        )
        return

    cellranger_submit_script = os.path.abspath(
        os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "../../../bin/cellranger/cellranger_count.sh",
        )
    )

    with tempfile.NamedTemporaryFile(
        delete=False, mode="w", dir=os.getenv("TEAM_TMP_DIR")
    ) as tmpfile:
        tmpfile_path = tmpfile.name

        for sample in valid_samples:
            command = f"{cellranger_submit_script} {sample} {version}"
            if not create_bam:
                command += " --no-bam"
            tmpfile.write(command + "\n")  # Write each command on a new line

    secho(f"Temporary command file created: {tmpfile_path}", "info")
    click.Abort()
    submit_lsf_job_array(
        command_file=tmpfile_path,
        job_name="cellranger_count_job_array",
        cpu=cpu,
        mem=mem,
        queue=queue,
    )

    secho(
        f"Command complete.",
        "success",
    )


if __name__ == "__main__":
    cmd()
