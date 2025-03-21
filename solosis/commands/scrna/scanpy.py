#!/usr/bin/env python3
import os
import subprocess

import click

from solosis.utils.farm import echo_message, irods_validation, log_command


@click.command("scanpy")
@click.option("--samplefile", required=True, help="Sample file text file")
@click.option(
    "--sample_basedir",
    required=False,
    default="/lustre/scratch126/cellgen/team298/sample_data/",
    help="sample database folder",
)
@click.pass_context
def cmd(ctx, samplefile, sample_basedir):
    """
    Basic Scanpy workflow for scRNA-seq data, generates Jupyter Notebook ... \n
    ----------------------

    Example: /lustre/scratch126/cellgen/team298/soft/bin/examples/irods_download.txt
    Input file should have 3 mandatory columns:
    1st column: sanger_id, 2nd column: sample_name, LAST column: irods path
    """
    log_command(ctx)
    echo_message(
        f"Starting Process: {click.style(ctx.command.name, bold=True, underline=True)}",
        "info",
    )

    # Path to the script
    shell_script = os.path.abspath(
        os.path.join(os.getenv("SCRIPT_BIN"), "../../../bin/scrna/scanpy/submit.sh")
    )
    env = os.environ.copy()
    env["solosis_dir"] = script_dir
    result = subprocess.run(
        [shell_script, sample_basedir, samplefile],
        env=env,
        capture_output=True,
        text=True,
    )
    echo_message(result.stdout)
    echo_message(result.stderr)
