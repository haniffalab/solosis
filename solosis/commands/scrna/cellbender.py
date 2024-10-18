#!/usr/bin/env python3

import os
import subprocess

import click


@click.command("cellbender")
@click.option("--samplefile", required=True, help="Sample file text file")
@click.option("--total_droplets_included", required=True, help="total_droplets_included")
def cmd(samplefile, total_droplets_included, **kwargs):
    """
    Cellbender Removes droplets and ambient RNA from scRNA seq data. \n
    --------------------------------- \n
          [ C E L L B E N D E R ]

    Cellbender Removes droplets and ambient RNA from scRNA seq data.
    Version:0.3.0.

    sample_ID: list of samples, CSV file format needed and header as 'samples'
    ---------------------------------
    """
    shell_cellbender_script = os.path.join(
        os.getcwd(), "/software/cellgen/team298/shared/solosis/bin/scrna/cellbender/submit.sh"
    )
    result_CB = subprocess.run(
        [shell_cellbender_script, samplefile, total_droplets_included],
        capture_output=True,
        text=True,
    )
    click.echo(result_CB.stdout)
