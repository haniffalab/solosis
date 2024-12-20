import uuid

import click

from solosis.commands.alignment import cellranger_arc, cellranger_count, starsolo
from solosis.commands.farm import farm
from solosis.commands.filesystem import disk_usage, file_count
from solosis.commands.irods import iget_cellranger, iget_fastqs
from solosis.commands.ncl_bsu import migrate
from solosis.commands.scrna import cellbender, merge_h5ad, scanpy

VERSION = "0.2.3"


# Styled output for the module name and version
module_name = click.style(f"{'SOLOSIS':^11}", bg="blue", fg="white", bold=True)
version_info = click.style(f"  ~  version {VERSION}")


@click.group()
@click.version_option(version=VERSION)
@click.pass_context
def cli(ctx):
    """Command line utility for the Cellular Genetics programme at the Wellcome Sanger Institute"""
    # Print a welcome message when the CLI tool is invoked
    click.echo(f"{module_name}{version_info}")

    # Access the execution_id from the context, or create a new one if not set
    execution_id = getattr(ctx.obj, "execution_id", None)
    if not execution_id:
        execution_id = str(uuid.uuid4())
        ctx.obj = {"execution_id": execution_id, "version": VERSION}


@cli.group()
def farm_cmds():
    """Farm related commands"""
    pass


# Alignment subgroup
@cli.group()
def alignment():
    """Commands for running alignment tools."""


alignment.add_command(cellranger_count.cmd, name="cellranger-count")
alignment.add_command(cellranger_arc.cmd, name="cellranger-arc")
alignment.add_command(starsolo.cmd, name="starsolo")


# Filesystem subgroup
@cli.group()
def filesystem():
    """Commands for file and directory operations."""


filesystem.add_command(disk_usage.cmd, name="disk-usage")
filesystem.add_command(file_count.cmd, name="file-count")


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


# farm
farm_cmds.add_command(farm.single_cmd)
farm_cmds.add_command(farm.run_ipynb)

if __name__ == "__main__":
    cli()
