import logging
import os
import tempfile

import click
import pandas as pd

from solosis.utils.env_utils import irods_auth
from solosis.utils.input_utils import collect_samples
from solosis.utils.logging_utils import debug, log
from solosis.utils.lsf_utils import lsf_options_sm, submit_lsf_job_array
from solosis.utils.state import logger
from solosis.utils.subprocess_utils import popen


@lsf_options_sm
@click.command("iget-cellranger")
@click.option("--sample", type=str, help="Sample ID (string).")
@click.option(
    "--samplefile",
    type=click.Path(exists=True),
    help="Path to a CSV or TSV file containing sample IDs.",
)
@debug
@log
def cmd(sample, samplefile, mem, cpu, queue, debug):
    """Downloads cellranger outputs from iRODS."""
    if debug:
        logger.setLevel(logging.DEBUG)

    ctx = click.get_current_context()
    logger.debug(
        f"Starting command: {click.style(ctx.command.name, bold=True, underline=True)}"
    )

    if not irods_auth():
        raise click.Abort()

    samples_to_download = []

    samples = collect_samples(sample, samplefile)
    with tempfile.NamedTemporaryFile(
        delete=False, mode="w", suffix=".txt", dir=os.environ["TEAM_TMP_DIR"]
    ) as tmpfile:
        logger.debug(f"Temporary command file created: {tmpfile.name}")
        os.chmod(tmpfile.name, 0o660)
        for sample in samples:
            sample_dir = os.path.join(os.getenv("TEAM_SAMPLES_DIR"), sample)
            cellranger_dir = os.path.join(
                os.getenv("TEAM_SAMPLES_DIR"), sample, "cellranger"
            )
            os.makedirs(cellranger_dir, exist_ok=True)
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

                for _, row in df.iterrows():
                    collection_type, path = row["collection_type"], row["path"]
                    if collection_type == "CellRanger":
                        collection_name = os.path.basename(path.rstrip("/"))
                        if not collection_name.strip():
                            logger.warning(
                                f"Could not determine collection name {path}"
                            )
                            continue
                        output_dir = os.path.join(cellranger_dir, collection_name)
                        if (
                            os.path.exists(output_dir)
                            and os.path.isdir(output_dir)
                            and os.listdir(output_dir)
                        ):
                            logger.warning(
                                f"Skipping {collection_name}, already exists in {cellranger_dir}"
                            )
                            continue

                        samples_to_download.append((sample, output_dir))
                        command = f"iget -r {path} {cellranger_dir} ; chmod -R g+w {cellranger_dir} >/dev/null 2>&1 || true"
                        tmpfile.write(command + "\n")
                        logger.info(
                            f'Collection "{collection_name}" for sample "{sample}" will be downloaded to: {output_dir}'
                        )

    submit_lsf_job_array(
        command_file=tmpfile.name,
        job_name="iget_cellranger_job_array",
        cpu=cpu,
        mem=mem,
        queue=queue,
    )

    if samples_to_download:
        log_file = os.path.join(os.getcwd(), "iget-cellranger.log")
        df = pd.DataFrame(samples_to_download, columns=["sample", "cellranger_dir"])
        df.to_csv(log_file, index=False)
        logger.info(f"Log file of output paths: {log_file}")


if __name__ == "__main__":
    cmd()
