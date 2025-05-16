# Import needed modules
import logging
import os
import tempfile

import click

# Import definitions from other solosis files (See `examples/README.md` for more information)
from solosis.utils.input_utils import collect_samples
from solosis.utils.logging_utils import debug, log
from solosis.utils.lsf_utils import lsf_job, submit_lsf_job_array
from solosis.utils.state import execution_uid, logger


# lsf_job is imported from `solosis/utils/lsf_utils.py`
@lsf_job(mem=64000, cpu=4, queue="normal")
# Build the click command
@click.command("command name ")
@click.option("--sample", type=str, help="Sample ID (string)")
@click.option(
    "--samplefile",
    type=click.Path(exists=True),
    help="Path to a CSV or TSV file containing sample IDs",
)
@click.option(
    "--optional",
    is_flag=True,
    default=False,
    help="optional flag ",
)
# Can add additional @click.option() here if needed.


@debug  # Imported from solosis/utils/logging_utils.py
@log  # Imported from solosis/utils/logging_utils.py
def cmd(
    sample, samplefile, optional, mem, cpu, queue, gpu, debug
):  # mem, cpu, queue, gpu imported from solosis/utils/lsf_utils.py

    # Include any checks/validations of input data

    # For more information, see ln 21 of `examples/README.md`
    # Use cellranger-count command as working example.

    # Define path to the command.sh file
    command_path = os.path.abspath(
        os.path.join(
            os.getenv("SCRIPT_BIN"),
            "command/command.sh",
        )
    )

    # Constructing the command that will be executed on the command line
    with tempfile.NamedTemporaryFile(
        delete=False, mode="w", suffix=".txt", dir=os.environ["TEAM_TMP_DIR"]
    ) as tmpfile:
        logger.debug(f"Temporary command file created: {tmpfile.name}")
        os.chmod(tmpfile.name, 0o660)
        for (
            sample
        ) in (
            valid_samples
        ):  # you would need to include validations yourself.. see ln 34
            command = f"{command_path} {sample['sample_id']} {sample['output_dir']} {version} {cpu} {mem}"
            if not optional:
                command += " --optional"
            tmpfile.write(command + "\n")

    # Submit job array
    submit_lsf_job_array(
        command_file=tmpfile.name,
        job_name="command_job_array",
        cpu=cpu,
        mem=mem,
        queue=queue,
        gpu=gpu,
    )


if __name__ == "__main__":
    cmd()
