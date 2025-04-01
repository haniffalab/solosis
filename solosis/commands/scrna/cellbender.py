import logging
import os
import tempfile

import click

from solosis.utils.input_utils import process_metadata_file
from solosis.utils.logging_utils import debug, log
from solosis.utils.lsf_utils import lsf_options_std, submit_lsf_job_array
from solosis.utils.state import logger

FASTQ_EXTENSIONS = [".fastq", ".fastq.gz"]
RAW_FEATURE_FILE = "raw_feature_bc_matrix.h5"  # The required file to check for


@lsf_options_std
@click.command("cellbender")
@click.option(
    "--metadata",
    type=click.Path(exists=True),
    help="Path to a CSV or TSV file containing metadata",
)
@click.option(
    "--total-droplets-included",
    type=int,
    required=False,
    default=False,
    help="Choose a number that goes a few thousand barcodes into the 'empty droplet plateau'",
)
@click.option(
    "--expected-cells",
    type=int,
    required=False,
    default=False,
    help="Base this on either the number of cells expected a priori from the experimental design",
)
@debug
@log
def cmd(metadata, total_droplets_included, expected_cells, mem, cpu, queue, debug):
    """Eliminate technical artifacts from scRNA-seq"""
    if debug:
        logger.setLevel(logging.DEBUG)

    ctx = click.get_current_context()
    logger.debug(
        f"Starting command: {click.style(ctx.command.name, bold=True, underline=True)}"
    )

    samples = process_metadata_file(metadata)

    valid_samples = []
    for sample in samples:
        sample_id = sample["sample_id"]
        cellranger_dir = sample["cellranger_dir"]
        output_dir = os.path.join(
            os.getenv("TEAM_SAMPLES_DIR"), sample_id, "cellbender"
        )

        # Check if cellranger_dir exists and contains the required file
        if os.path.exists(cellranger_dir) and os.path.isfile(
            os.path.join(cellranger_dir, RAW_FEATURE_FILE)
        ):
            if os.path.exists(output_dir) and os.path.isfile(
                os.path.join(output_dir, "cb.h5")
            ):
                logger.warning(
                    f"Cellbender output already exists for sample {sample} in {output_dir}. Skipping this sample"
                )
            else:
                valid_samples.append(
                    {
                        "sample_id": sample_id,
                        "cellranger_dir": cellranger_dir,
                        "output_dir": output_dir,
                    }
                )
        else:
            logger.warning(
                f"Required file {RAW_FEATURE_FILE} not found in {cellranger_dir} for sample {sample}. Skipping this sample"
            )

    if not valid_samples:
        logger.error(f"No valid samples found. Exiting")
        return

    script_path = os.path.abspath(
        os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "../../../bin/cellbender/cellbender.sh",
        )
    )

    with tempfile.NamedTemporaryFile(
        delete=False, mode="w", suffix=".txt", dir=os.environ["TEAM_TMP_DIR"]
    ) as tmpfile:
        logger.debug(f"Temporary command file created: {tmpfile.name}")
        os.chmod(tmpfile.name, 0o660)
        for sample in valid_samples:
            command = f"{script_path} {sample['sample_id']} {sample['output_dir']} {sample['cellranger_dir']} {cpu} {mem}"
            # Add optional arguments if specified
            if total_droplets_included is not None:
                command += f" --total-droplets-included {total_droplets_included}"
            if expected_cells is not None:
                command += f" --expected-cells {expected_cells}"
            tmpfile.write(command + "\n")

    submit_lsf_job_array(
        command_file=tmpfile.name,
        job_name="cellbender_job_array",
        cpu=cpu,
        mem=mem,
        queue=queue,
    )


if __name__ == "__main__":
    cmd()
