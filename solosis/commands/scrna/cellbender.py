#!/usr/bin/env python3

import os
import subprocess

import click


@click.command("cellbender")
@click.option("--samplefile", required=True, help="Sample file text file")
@click.option(
    "--total_droplets_included", required=True, help="total_droplets_included"
)
def cmd(samplefile, total_droplets_included, **kwargs):
    """
    Removes droplets & ambient RNA from scRNA-seq data ... \n
    --------------------------------- \n
    Cellbender (0.3.0.) Removes droplets & ambient RNA from scRNA seq data.

    """
    shell_cellbender_script = os.path.join(
        os.getcwd(),
        "bin/scrna/cellbender/submit.sh",
    )
    result_CB = subprocess.run(
        [shell_cellbender_script, samplefile, total_droplets_included],
        capture_output=True,
        text=True,
    )
    click.echo(result_CB.stdout)
