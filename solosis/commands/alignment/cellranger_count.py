import logging
import os
import tempfile

import click

from solosis.utils.input_utils import collect_samples
from solosis.utils.logging_utils import debug, log
from solosis.utils.lsf_utils import lsf_job, submit_lsf_job_array
from solosis.utils.state import execution_uid, logger

FASTQ_EXTENSIONS = [".fastq", ".fastq.gz"]


@lsf_job(mem=64000, cpu=4, queue="long", time="12:00")
@click.command("cellranger-count")
@click.option("--sample", type=str, help="Sample ID (string)")
@click.option(
    "--samplefile",
    type=click.Path(exists=True),
    help=(
        "Path to a CSV or TSV file containing sample IDs as a comma-separated (.csv) "
        "or tab-separated (.tsv) file. The file must have a column named 'sample_id' containing the sample IDs.\n\n"
        "Example CSV format:\n"
        "sample_id\n"
        "s12345\n"
        "s67890"
    ),
)
@click.option(
    "--create-bam",
    is_flag=True,
    default=False,
    help="Generate BAM files for each sample",
)
@click.option(
    "--chemistry",
    type=click.Choice(
        [
            "threeprime",
            "fiveprime",
            "SC5P-R2",
            "SC5P-PE",
            "SC5P-PE-v3",
            "SC5P-R2",
            "SC5P-R2-v3",
            "SC3Pv1",
            "SC3Pv3",
            "SC3Pv2",
            "SC3Pv4",
            "SC3Pv3LT",
            "SC3Pv3HT",
            "SC-FB",
            "SFRP",
            "MFRP",
            "ARC-v1",
        ]
    ),
    # type=str,
    help="Chemistry assay to define",
)
@click.option(
    "--version",
    type=str,
    default="7.2.0",
    help="Cell Ranger version to use (e.g., '7.2.0')",
)
@debug
@log
def cmd(
    sample,
    samplefile,
    create_bam,
    chemistry,
    version,
    mem,
    cpu,
    queue,
    gpu,
    gpumem,
    gpunum,
    gpumodel,
    time,
    debug,
):
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
            log_file = os.path.join(output_dir, sample, "_log")
            outs_dir = os.path.join(output_dir, "outs")
            matrix_dir = os.path.join(outs_dir, "filtered_feature_bc_matrix")

            # If no output directory, sample is valid to run
            if not os.path.exists(output_dir):
                valid_samples.append(
                    {
                        "sample_id": sample,
                        "output_dir": output_dir,
                        "fastq_dir": fastq_dir,
                    }
                )
                continue

            # If output dir exists but no log file, job likely failed/killed
            if not os.path.exists(log_file):
                logger.error(
                    f"Output directory exists for {sample}, but no log file found. "
                    f"suggesting cellranger was unsuccessful. "
                    f"Inspect {output_dir} and remove before re-running."
                )
                continue  # Do NOT add to valid_samples

            # If log exists but no success message or missing matrix, it's incomplete
            with open(log_file, "r") as lf:
                log_content = lf.read()
                if (
                    "Pipestance completed successfully!" not in log_content
                    and not os.path.exists(matrix_dir)
                ):
                    logger.warning(
                        f"Incomplete CellRanger run detected for {sample}. "
                        f"Inspect {output_dir} and remove before re-running."
                    )
                    continue

            # If we reach this point, the sample has already been successfully processed
            logger.warning(
                f"CellRanger already completed successfully for {sample}. Skipping."
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
            command = f"{cellranger_count_path} {sample['sample_id']} {sample['output_dir']} {sample['fastq_dir']} {version} {cpu} {mem} {time}"
            if not create_bam:
                command += " --no-bam"
            if chemistry:
                command += f" --chemistry {chemistry}"
            tmpfile.write(command + "\n")

    submit_lsf_job_array(
        command_file=tmpfile.name,
        job_name="cellranger_count_job_array",
        cpu=cpu,
        mem=mem,
        queue=queue,
        gpu=gpu,
        gpumem=gpumem,
        gpunum=gpunum,
        gpumodel=gpumodel,
    )


if __name__ == "__main__":
    cmd()
