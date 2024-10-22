"""
process_merscope.py
====================================
Processes MERSCOPE output
"""

from importlib.metadata import version as pkg_version

import click

from solosis.commands.alignment import cellranger, cellrangerARC, starsolo
from solosis.commands.irods import pull_cellranger, pull_fastqs
from solosis.commands.scrna import cellbender, merge_h5ad, scanpy

VERSION = "0.2.1"


@click.group()
@click.version_option(version=VERSION)
def cli():
    """Command line utility for the Cellular Genetics
    programme at the Wellcome Sanger Institute"""
    pass


# Alignment
cli.add_command(cellranger.cmd)
cli.add_command(cellrangerARC.cmd)
cli.add_command(starsolo.cmd)

# iRods
cli.add_command(pull_fastqs.cmd)
cli.add_command(pull_cellranger.cmd)

# scrna
cli.add_command(cellbender.cmd)
cli.add_command(scanpy.cmd)
cli.add_command(merge_h5ad.cmd)

if __name__ == "__main__":
    cli()
