#!/usr/bin/env python3
import os
import subprocess

import click

from solosis.utils.farm import echo_message, irods_validation, log_command
from solosis.utils.logging_utils import debug
from solosis.utils.lsf_utils import lsf_job, lsf_options_sm, _assign_job_name
from solosis.utils.env_utils import create_solosis_dirs

@click.command("scanpy")

@click.option("--samplefile", 
              required=True, 
              type=click.Path(exists=True),
              help="Sample file text file")
@click.option(
    "--sample_basedir",
    required=False,
    default="/lustre/scratch126/cellgen/team298/data/samples/",
    help="sample database folder",
)
@lsf_job(mem=64000)
@click.pass_context
def cmd(ctx, samplefile, sample_basedir, **kwargs):
    """
    Basic Scanpy workflow for scRNA-seq data, generates Jupyter Notebook ... \n
    ----------------------

    Example: (defunct) /lustre/scratch126/cellgen/team298/soft/bin/examples/irods_download.txt
    Input file should have 1 mandatory columns:
    1st column: sample_id
    Any other column would be appended to your adata.obs dataframe
    """
    #log_command(ctx)
    echo_message(
        f"Starting Process: {click.style(ctx.command.name, bold=True, underline=True)}",
        "info",
    )

    # Path to the script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    shell_script = os.path.abspath(
        os.path.join(script_dir, "../../../bin/scrna/scanpy/submit.sh")
    )
    create_solosis_dirs()
    #_assign_job_name("scanpy", ctx)

    env = os.environ.copy()
    env["solosis_dir"] = script_dir

    result = subprocess.run(
        [shell_script, sample_basedir, samplefile],
        env={**env, **kwargs},
        capture_output=True,
        text=True,
    )
    echo_message(result.stdout)
    echo_message(result.stderr)
