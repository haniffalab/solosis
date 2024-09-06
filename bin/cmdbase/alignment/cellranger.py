#!/usr/bin/env python3

import os
import subprocess

import click

SHELL_SCRIPT_BASE = os.environ["SHELL_SCRIPT_BASE"]


@click.command("cellranger")
def cellranger():
    """
    Cellranger aligns sc-rna seq reads...
    --------------------------------- \n
        [ C E L L R A N G E R]

    Cellranger sample demultiplexing, barcode processing, single cell 3' & 5' gene counting, V(D)J transcript sequence assembly>
    Version:7.2.0.

    sample_ID: list of samples, CSV file format needed and header as 'samples'
    ---------------------------------
    """
    shell_cellranger_script = os.path.join(
        SHELL_SCRIPT_BASE, "test..submit_cellranger"
    )  # can we change script base to sc-voyage d>
    result_CR = subprocess.run(
        [shell_cellranger_script], capture_output=True, text=True
    )
    click.echo(result_CR.stdout)
