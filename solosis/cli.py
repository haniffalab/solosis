from importlib.metadata import version as pkg_version

import click

from solosis.commands.alignment import cellranger_arc, cellranger_count, starsolo
from solosis.commands.irods import iget_cellranger, iget_fastqs
from solosis.commands.ncl_bsu import migrate
from solosis.commands.scrna import cellbender, merge_h5ad, scanpy
from solosis.commands.utilities import disk_usage

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


# Alignment subgroup
@cli.group()
def alignment():
    """Commands for running alignment tools."""


alignment.add_command(cellranger_count.cmd, name="cellranger-count")
alignment.add_command(cellranger_arc.cmd, name="cellranger-arc")
alignment.add_command(starsolo.cmd, name="starsolo")


# iRODS subgroup
@cli.group()
def irods():
    """Commands for working with iRODS."""


irods.add_command(iget_fastqs.cmd, name="iget-fastqs")
irods.add_command(iget_cellranger.cmd, name="iget-cellranger")


# NCL_BSU subgroup
@cli.group()
def ncl_bsu():
    """Commands for Newcastle University BSU."""


ncl_bsu.add_command(migrate.cmd, name="migrate")


# scRNA subgroup
@cli.group()
def sc_rna():
    """Commands for single-cell RNA-seq workflows."""


sc_rna.add_command(cellbender.cmd, name="cellbender")
sc_rna.add_command(scanpy.cmd, name="scanpy")
sc_rna.add_command(merge_h5ad.cmd, name="merge-h5ad")


# utilities
cli.add_command(disk_usage.cmd)

if __name__ == "__main__":
    cli()
