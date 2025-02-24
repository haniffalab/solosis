import os
import subprocess
import tempfile

import click
import pandas as pd

from solosis.utils.env_utils import irods_auth
from solosis.utils.input_utils import collect_samples
from solosis.utils.logging_utils import secho
from solosis.utils.lsf_utils import lsf_options, submit_lsf_job_array


@lsf_options
@click.command("iget-cellranger")
@click.option("--sample", type=str, help="Sample ID (string).")
@click.option(
    "--samplefile",
    type=click.Path(exists=True),
    help="Path to a CSV or TSV file containing sample IDs.",
)
def cmd(sample, samplefile, mem, cpu, queue):
    """Downloads cellranger outputs from iRODS."""
    ctx = click.get_current_context()
    secho(
        f"Starting Process: {click.style(ctx.command.name, bold=True, underline=True)}",
        "info",
    )

    irods_auth()

    samples = collect_samples(sample, samplefile)

    with tempfile.NamedTemporaryFile(
        delete=False, mode="w", suffix=".txt", dir=os.environ["TEAM_TMP_DIR"]
    ) as tmpfile:
        secho(f"Temporary command file created: {tmpfile.name}", "info")
        os.chmod(tmpfile.name, 0o660)
        for sample in samples:
            sample_dir = os.path.join(os.getenv("TEAM_SAMPLES_DIR"), sample)
            cellranger_dir = os.path.join(
                os.getenv("TEAM_SAMPLES_DIR"), sample, "cellranger"
            )
            os.makedirs(cellranger_dir, exist_ok=True)
            report_path = os.path.join(sample_dir, "imeta_report.csv")

            # Path to the script
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

                # Now read the report and process it
                if os.path.exists(report_path):
                    # Load the report as a dataframe
                    df = pd.read_csv(
                        report_path, header=None, names=["collection_type", "path"]
                    )

                    # Loop through each row in the dataframe
                    for _, row in df.iterrows():
                        collection_type, path = row["collection_type"], row["path"]
                        if collection_type == "CellRanger":
                            collection_name = os.path.basename(path.rstrip("/"))
                            if not collection_name.strip():
                                secho(
                                    f"Could not determine collection name {path}",
                                    "warn",
                                )
                                continue
                            output_dir = os.path.join(cellranger_dir, collection_name)
                            if (
                                os.path.exists(output_dir)
                                and os.path.isdir(output_dir)
                                and os.listdir(output_dir)
                            ):
                                secho(
                                    f"Skipping {collection_name}, already exists in {cellranger_dir}"
                                    "warn",
                                )
                                continue

                            command = f"iget -r {path} {cellranger_dir}"
                            tmpfile.write(command + "\n")

            except subprocess.CalledProcessError as e:
                # Catch subprocess-specific errors (e.g., command failed with non-zero exit code)
                secho(
                    f"Command '{e.cmd}' failed with return code {e.returncode}", "error"
                )
                secho(f"Standard Error: {e.stderr}", "error")
                secho(f"Standard Output: {e.stdout}", "info")
            except Exception as e:
                # Catch any unexpected errors
                secho(f"Unexpected error: {str(e)}", "error")

    # submit_lsf_job_array(
    #     command_file=tmpfile.name,
    #     job_name="iget_cellranger_job_array",
    #     cpu=cpu,
    #     mem=mem,
    #     queue=queue,
    # )


if __name__ == "__main__":
    cmd()
