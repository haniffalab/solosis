#!/usr/bin/env python3
import os
import subprocess

import click

SHELL_SCRIPT_BASE = os.environ["SHELL_SCRIPT_BASE"]
HL_IRODS_DOWNLOAD = os.environ["HL_IRODS_DOWNLOAD"]


@click.command("scanpy")
@click.option("--samplefile", required=True, help="Sample file text file")
@click.option(
    "--sample_basedir",
    required=False,
    default=HL_IRODS_DOWNLOAD,
    help="sample database folder",
)
def scanpyrun(samplefile, sample_basedir):
    """
    Basic scanpy run

    Example: /lustre/scratch126/cellgen/team298/soft/bin/examples/irods_download.txt
    Input file should have 3 mandatory columns
    1st column: sanger_id
    2nd column: sample_name
    LAST column: irods path
    You can have any column in between

    pBCN14844712 BK31_1 /seq/illumina/runs/49/..../cellranger710multi....
    pBCN14844713 BK31_2 /seq/illumina/runs/49/..../cellranger710multi....
    pBCN14844714 BK31_3 /seq/illumina/runs/49/..../cellranger710multi....
    pBCN14844715 BK31_4 /seq/illumina/runs/49/..../cellranger710multi....

    ----------------------
    Use the same sample file you used for irods/pull-processed
    """
    shell_script = os.path.join(SHELL_SCRIPT_BASE, "rna..scanpy")
    result = subprocess.run(
        [shell_script, sample_basedir, samplefile], capture_output=True, text=True
    )
    click.echo(result.stdout)
    click.echo(result.stderr)
