#!/usr/bin/env python3
import os
import subprocess

import click


@click.command("merge-h5ad")
@click.option("--samplefile", required=True, help="Sample file text file")
@click.option(
    "--merged_filename", required=True, help="Output file name: Eg. merged.h5ad"
)
def cmd(samplefile, merged_filename, **kwargs):
    """
    Merging multiple h5ads objects...
    ---------------------------------
    Please run `rna scanpy --samplefile ...` command first.

    Example: /lustre/scratch126/cellgen/team298/soft/bin/examples/irods_download.txt
    Input file should have 3 mandatory columns:
    1st column: sanger_id, 2nd column: sample_name, LAST column: irods path

    """
    shell_script = os.path.join(
        os.getcwd(),
        "bin/scrna/merge-h5ad/submit.sh",
    )
    result = subprocess.run(
        [shell_script, samplefile, merged_filename], capture_output=True, text=True
    )
    click.echo(result.stdout)
    click.echo(result.stderr)
