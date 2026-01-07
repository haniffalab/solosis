import logging
import os
import tempfile

import click

from solosis.utils.input_utils import process_metadata_file
from solosis.utils.logging_utils import debug, log
from solosis.utils.lsf_utils import lsf_job, submit_lsf_job_array
from solosis.utils.state import execution_uid, logger

# Define the environment
conda_env = "/software/cellgen/team298/shared/envs/hlb-conda/scrna"
sc_base1_path = os.path.abspath(
    os.path.join(
        os.getenv("NOTEBOOKS_DIR"),
        "sc_base1.ipynb",
    )
)


@lsf_job(mem=20000, cpu=1, queue="normal", time="04:00")
@click.command("scanpy")
@click.option("--metadata", required=True, help="metadata csv file")
@click.option("--outpt_folder_path", required=True, help="Folder to save outputs")
@click.option(
    "--job_name",
    required=False,
    type=str,
    default="scanpy",
    help="Optional name for the LSF job. Defaults to scanpy_<uid>.",
)
@debug
@log
def cmd(
    metadata,
    job_name,
    outpt_folder_path,
    mem,
    cpu,
    queue,
    gpu,
    gpumem,
    gpunum,
    gpumodel,
    time,
    debug,
    **kwargs,
):
    """
    Submit Scanpy workflow for scRNA-seq data as a job on the compute farm.

    Input samplefile should have 3 mandatory columns:
    1st column: sample_id
    2nd column: sanger_id
    3rd column: h5_path

    Example csv:
        sample_id,sanger_id,cellranger_dir
        WS_wEMB10202353,WS_wEMB10202353,/lustre/scratch124/cellgen/haniffa/data/samples/WS_wEMB10202353/cellranger/cellranger601_count_37876_WS_wEMB10202353_GRCh38-2020-A
        WS_wEMB10202354,WS_wEMB10202354,/lustre/scratch124/cellgen/haniffa/data/samples/WS_wEMB10202354/cellranger/cellranger601_count_37876_WS_wEMB10202354_GRCh38-2020-A

    Example command: solosis-cli  scrna scanpy --metadata samples.csv --outpt_folder_path rna_scanpy
    """
    if debug:
        logger.setLevel(logging.DEBUG)

    ctx = click.get_current_context()
    logger.debug(
        f"Starting command: {click.style(ctx.command.name, bold=True, underline=True)}"
    )
    job_name = execution_uid if job_name == "default" else f"{job_name}_{execution_uid}"
    logger.debug(f"Job name: {job_name}")

    samples = process_metadata_file(
        metadata, required_columns={"sample_id", "sanger_id", "h5_path"}
    )

    # Check for invalid h5 paths
    for s in samples:
        h5_path = s["h5_path"]
        if not h5_path.endswith(".h5"):
            raise click.ClickException(
                f"Invalid h5_path detected (must end with .h5): {h5_path}"
            )

    valid_samples = []
    for sample in samples:
        sample_id = sample["sample_id"]
        sanger_id = sample["sanger_id"]
        h5_path = sample["h5_path"]
        if not os.path.exists(h5_path):
            logger.error(
                f"h5 file does not exist: {h5_path} for sample: {sample_id}. Skipping."
            )
            continue  # skip this sample entirely

        # Path of the expected output notebook
        output_dir = outpt_folder_path
        os.makedirs(output_dir, exist_ok=True)
        output_notebook = os.path.join(output_dir, f"{sample_id}_{sanger_id}.ipynb")
        if os.path.exists(output_notebook):
            logger.warning(
                f"Notebook for {sample_id} already exists at {output_notebook}. Skipping."
            )
            continue  # skip this sample

        valid_samples.append(
            {
                "sample_id": sample_id,
                "sanger_id": sanger_id,
                "h5_path": h5_path,
                "output_dir": output_dir,
            }
        )

    if not valid_samples:
        logger.error(f"No valid samples found. Exiting")
        return

    with tempfile.NamedTemporaryFile(
        delete=False, mode="w", suffix=".txt", dir=os.environ["TEAM_TMP_DIR"]
    ) as tmpfile:
        logger.debug(f"Temporary command file created: {tmpfile.name}")
        os.chmod(tmpfile.name, 0o660)

        # Submit job for each valid sample
        for sample in valid_samples:
            sample_id = sample["sample_id"]
            sanger_id = sample["sanger_id"]
            h5_path = sample["h5_path"]
            output_dir = sample["output_dir"]

            # Build papermill command
            command = (
                f"module load cellgen/conda && "
                f"source activate {conda_env} && "
                f"python -m ipykernel install --user --name hlb_rna --display-name 'HLB RNA (conda)' && "
                f"papermill {sc_base1_path} -k hlb_rna "
                f"{output_notebook} "
                f"-p sample_id '{sample_id}' "
                f"-p sanger_id '{sanger_id}' "
                f"-p h5_file '{h5_path}' "
                f"-p outpt_folder_path '{outpt_folder_path}' "
                "--log-output"
            )
            tmpfile.write(command + "\n")

    submit_lsf_job_array(
        command_file=tmpfile.name,
        job_name=job_name,
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
