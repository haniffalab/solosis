#!/usr/bin/env python3
import os
import subprocess

import click


@click.command("scanpy")
@click.option("--samplefile", required=True, help="Sample file text file")
@click.option(
    "--sample_basedir",
    required=False,
    default="/lustre/scratch126/cellgen/team298/sample_data/",
    help="sample database folder",
)
def cmd(samplefile, sample_basedir):
    """
    Basic Scanpy workflow for scRNA seq data, generates Jupyter Notebook ...
    ----------------------

    Example: /lustre/scratch126/cellgen/team298/soft/bin/examples/irods_download.txt \n
    Input file should have 3 mandatory columns \n
    1st column: sanger_id \n
    2nd column: sample_name \n
    LAST column: irods path \n

    :param samplefile: Input file (.txt)
    :param sample_basedir: Path to base directory
    ----------------------
    """
    shell_script = os.path.join(
        os.getcwd(),
        "/software/cellgen/team298/shared/solosis/bin/scrna/scanpy/submit.sh",
    )
    result = subprocess.run(
        [shell_script, sample_basedir, samplefile], capture_output=True, text=True
    )
    click.echo(result.stdout)
    click.echo(result.stderr)