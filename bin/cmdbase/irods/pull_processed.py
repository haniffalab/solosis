#!/usr/bin/env python3
import os
import subprocess

import click

SHELL_SCRIPT_BASE = os.environ["SHELL_SCRIPT_BASE"]


@click.command("pull-processed")
@click.option("--samplefile", required=True, help="Sample file text file")
@click.option(
    "--retainbam",
    default=False,
    is_flag=True,
    required=False,
    help="Download alignment bam file",
)
@click.option(
    "--overwrite",
    default=False,
    is_flag=True,
    required=False,
    help="Overwrite existing folder contents",
)
def pull_processed(samplefile, retainbam, overwrite):
    """
    Downloads processed irods data or any folder from irods
    and saves it to $HL_IRODS_DOWNLOAD. This is set when you load module
    Requires a sample file.

    -----------------------

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

    Suggested way. Open Haniffa sample tracker excel file.
    Copy/paste your project sample rows to a local excel file.
    Remove columns to match required format.

    """
    print("Using irods to download data")
    print("If you have a large set of files, this command will take a while to run")
    shell_script = os.path.join(SHELL_SCRIPT_BASE, "irods..download_processed")
    overwrite = str(overwrite * 1)
    retainbam = str(retainbam * 1)
    result = subprocess.run(
        [shell_script, samplefile, retainbam, overwrite], capture_output=True, text=True
    )
    click.echo(result.stdout)
    click.echo(result.stderr)
