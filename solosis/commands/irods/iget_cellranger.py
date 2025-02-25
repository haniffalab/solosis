import logging
import os
import subprocess
import tempfile

import click
import pandas as pd

from solosis.utils.env_utils import irods_auth
from solosis.utils.input_utils import collect_samples
from solosis.utils.logging_utils import debug
from solosis.utils.lsf_utils import lsf_options, submit_lsf_job_array
from solosis.utils.state import logger


@lsf_options
@debug
@click.command("iget-cellranger")
@click.option("--sample", type=str, help="Sample ID (string).")
@click.option(
    "--samplefile",
    type=click.Path(exists=True),
    help="Path to a CSV or TSV file containing sample IDs.",
)
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

    samples = collect_samples(sample, samplefile)
    with tempfile.NamedTemporaryFile(
        delete=False, mode="w", suffix=".txt", dir=os.environ["TEAM_TMP_DIR"]
    ) as tmpfile:
        logger.info(f"Temporary command file created: {tmpfile.name}")
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
                    os.path.dirname(os.path.abspath(__file__)),
                    "../../../bin/irods/imeta_report.sh",
                )
            )

            try:
                subprocess.run(
                    [imeta_report_script, sample, report_path],
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )

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

                            command = f"iget -r {path} {cellranger_dir}"
                            tmpfile.write(command + "\n")

            except subprocess.CalledProcessError as e:
                logger.error(
                    f"Command '{e.cmd}' failed with return code {e.returncode}"
                )
                logger.error(f"Standard Error: {e.stderr}")
                logger.info(f"Standard Output: {e.stdout}")
            except Exception as e:
                logger.error(f"Unexpected error: {str(e)}")

    submit_lsf_job_array(
        command_file=tmpfile.name,
        job_name="iget_cellranger_job_array",
        cpu=cpu,
        mem=mem,
        queue=queue,
    )


if __name__ == "__main__":
    cmd()
