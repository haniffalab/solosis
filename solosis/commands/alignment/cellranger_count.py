import logging
import os
import tempfile

import click

from solosis.utils.input_utils import collect_samples
from solosis.utils.logging_utils import debug
from solosis.utils.lsf_utils import lsf_options_std, submit_lsf_job_array
from solosis.utils.state import logger

FASTQ_EXTENSIONS = [".fastq", ".fastq.gz"]


@lsf_options_std
@debug
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
def cmd(sample, samplefile, create_bam, version, mem, cpu, queue, debug):
    """scRNA-seq mapping and quantification"""
    if debug:
        logger.setLevel(logging.DEBUG)

    ctx = click.get_current_context()
    logger.debug(
        f"Starting command: {click.style(ctx.command.name, bold=True, underline=True)}"
    )
    logger.debug(f"Loading Cell Ranger Count version {version}")

    samples = collect_samples(sample, samplefile)
    valid_samples = []
    for sample in samples:
        fastq_dir = os.path.join(os.getenv("TEAM_SAMPLES_DIR"), sample, "fastq")
        output_dir = os.path.join(
            os.getenv("TEAM_SAMPLES_DIR"),
            sample,
            "cellranger",
            f"solosis_{version.replace('.', '')}",
        )

        if os.path.exists(fastq_dir) and any(
            f.endswith(ext) for ext in FASTQ_EXTENSIONS for f in os.listdir(fastq_dir)
        ):
            if os.path.exists(output_dir):
                logger.warning(
                    f"CellRanger output already exists for sample {sample} in {output_dir}. Skipping this sample"
                )
            else:
                valid_samples.append(
                    {
                        "sample_id": sample,
                        "output_dir": output_dir,
                        "fastq_dir": fastq_dir,
                    }
                )
        else:
            logger.warning(
                f"No FASTQ files found for sample {sample} in {fastq_dir}. Skipping this sample"
            )

    if not valid_samples:
        logger.error(f"No valid samples found. Exiting")
        raise click.Abort()

    cellranger_count_path = os.path.abspath(
        os.path.join(
            os.getenv("SCRIPT_BIN"),
            "cellranger/cellranger_count.sh",
        )
    )

    with tempfile.NamedTemporaryFile(
        delete=False, mode="w", suffix=".txt", dir=os.environ["TEAM_TMP_DIR"]
    ) as tmpfile:
        logger.debug(f"Temporary command file created: {tmpfile.name}")
        os.chmod(tmpfile.name, 0o660)
        for sample in valid_samples:
            command = f"{cellranger_count_path} {sample['sample_id']} {sample['output_dir']} {sample['fastq_dir']} {version} {cpu} {mem}"
            if not create_bam:
                command += " --no-bam"
            tmpfile.write(command + "\n")

    submit_lsf_job_array(
        command_file=tmpfile.name,
        job_name="cellranger_count_job_array",
        cpu=cpu,
        mem=mem,
        queue=queue,
    )


if __name__ == "__main__":
    cmd()
