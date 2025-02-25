import os
import tempfile

import click

from solosis.utils.input_utils import process_metadata_file
from solosis.utils.logging_utils import secho
from solosis.utils.lsf_utils import lsf_options, submit_lsf_job_array


@lsf_options
@click.command("cellbender")
@click.option(
    "--metadata",
    type=click.Path(exists=True),
    help="Path to a CSV or TSV file containing metadata",
)
def cmd(metadata, mem, cpu, queue):
    """Eliminate technical artifacts from scRNA-seq"""
    ctx = click.get_current_context()
    secho(
        f"Starting Process: {click.style(ctx.command.name, bold=True, underline=True)}",
        "info",
    )

    samples = process_metadata_file(metafile)

    valid_samples = []
    for sample in samples:
        fastq_dir = os.path.join(os.getenv("TEAM_SAMPLES_DIR"), sample, "cellranger")
        output_dir = os.path.join(os.getenv("TEAM_SAMPLES_DIR"), sample, "cellbender")

        if os.path.exists(fastq_dir) and any(
            f.endswith(ext) for ext in FASTQ_EXTENSIONS for f in os.listdir(fastq_dir)
        ):
            if os.path.exists(output_dir):
                secho(
                    f"CellRanger output already exists for sample {sample} in {output_dir}. Skipping this sample",
                    "warn",
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
            secho(
                f"No FASTQ files found for sample {sample} in {fastq_dir}. Skipping this sample",
                "warn",
            )

    if not valid_samples:
        secho(f"No valid samples found. Exiting", "error")
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
        secho(f"Temporary command file created: {tmpfile.name}", "info")
        os.chmod(tmpfile.name, 0o660)
        for sample in valid_samples:
            command = f"{script_path} {sample['sample_id']} {sample['output_dir']} {sample['fastq_dir']} {version} {cpu} {mem}"
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
