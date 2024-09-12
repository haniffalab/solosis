#!/usr/bin/env python3

import os
import subprocess

import click

SHELL_SCRIPT_BASE = os.environ["SHELL_SCRIPT_BASE"]


@click.command()
@click.option("--samplefile", required=True, help="Sample file text file")
def starsolo(samplefile):
    """
    STARsolo aligns sc-rna seq reads...
    --------------------------------- \n
        [ S T A R S O L O ]

    STARsolo ...
    Version:2.7.11b

    sample_ID: list of samples, CSV file format needed and header as 'samples'
    ---------------------------------
    """
    shell_starsolo_script = os.path.join(
        SHELL_SCRIPT_BASE, "alignment..submit_starsolo"
    )  # can we change script base to sc-voyage dir
    result_STAR = subprocess.run(
        [shell_starsolo_script, samplefile], capture_output=True, text=True
    )
    click.echo(result_STAR.stdout)
