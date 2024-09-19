#!/usr/bin/env python3

import os
import subprocess

import click

SHELL_SCRIPT_BASE = os.environ["SHELL_SCRIPT_BASE"]


@click.command("cellranger")
@click.option("--samplefile", required=True, help="Sample file text file")
@click.option(
    "--includebam",
    is_flag=True,
    default=False,
    help="Include BAM files (removes --no-bam from cellranger)",
)
# @click.option('--includebam', required=False, show_default=True, default=False, help="Pull Bam files")
def cellranger(samplefile, includebam):
    """
    Cellranger aligns sc-rna seq reads... \n
    --------------------------------- \n
        [ C E L L R A N G E R]

    Cellranger sample demultiplexing, barcode processing, single cell 3' & 5' gene counting, V(D)J transcript sequence assembly \n
    Version:7.2.0.

    sample_ID: list of samples, CSV file format needed and header as 'samples'
    ---------------------------------
    """
    shell_cellranger_script = os.path.join(
        SHELL_SCRIPT_BASE, "alignment..submit_cellranger"
    )  # can we change script base to sc-voyage dir
    # Pass the includebam flag as an argument to the bash script
    includebam = str(includebam * 1)
    includebam_str = "1" if includebam else "0"
    result_CR = subprocess.run(
        [shell_cellranger_script, samplefile, includebam],
        capture_output=True,
        text=True,
    )
    click.echo(result_CR.stdout)
