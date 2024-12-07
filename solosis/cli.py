from importlib.metadata import version as pkg_version

import click

from solosis.commands.alignment import cellranger, cellrangerARC, starsolo
from solosis.commands.irods import pull_cellranger, pull_fastqs
from solosis.commands.scrna import cellbender, merge_h5ad, scanpy
from solosis.commands.farm import farm

VERSION = "0.2.3"

# Styled output for the module name and version
module_name = click.style(f"{'SOLOSIS':^11}", bg="blue", fg="white", bold=True)
version_info = click.style(f"  ~  version {VERSION}")


@click.group()
@click.version_option(version=VERSION)
def cli():
    """Command line utility for the Cellular Genetics
    programme at the Wellcome Sanger Institute"""

    # Print a welcome message when the CLI tool is invoked
    click.echo(click.echo(f"{module_name}{version_info}"))
    pass


@cli.group()
def farm_cmds():
    """Farm related commands"""
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

# farm
farm_cmds.add_command(farm.cmd)

if __name__ == "__main__":
    cli()
