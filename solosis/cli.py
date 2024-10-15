from importlib.metadata import version as pkg_version

import click

from solosis.commands.alignment import cellranger, cellrangerARC, starsolo
from solosis.commands.irods import pull_cellranger, pull_fastqs


@click.group()
@click.version_option(version=pkg_version("solosis"))
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

# RNA
# cli.add_command(rna.cmd)

if __name__ == "__main__":
    cli()
