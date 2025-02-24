import click

from solosis.commands.alignment import cellranger_arc_count, cellranger_count, starsolo
from solosis.commands.irods import iget_cellranger, iget_fastqs, imeta_report, lsf
from solosis.commands.scrna import cellbender, merge_h5ad, qc_basic, scanpy
from solosis.utils.env_utils import validate_env
from solosis.utils.state import execution_uid, logger, version

# Styled output for the module name and version
module_name = click.style(f"{'SOLOSIS':^11}", bg="blue", fg="white", bold=True)
version_info = click.style(f"  ~  version {version}")


@click.group()
@click.pass_context
def cli(ctx):
    """Command line utility for the Cellular Genetics programme at the Wellcome Sanger Institute"""
    click.echo(f"{module_name}{version_info}")
    validate_env()
    logger.info(f"Logger initialized at startup with execution_uid: {execution_uid}")


@cli.group()
def alignment():
    """Commands for running alignment tools."""
    pass


alignment.add_command(cellranger_count.cmd, name="cellranger-count")
alignment.add_command(cellranger_arc_count.cmd, name="cellranger-arc-count")
alignment.add_command(starsolo.cmd, name="starsolo")


@cli.group()
def irods():
    """Commands for working with iRODS."""
    pass


irods.add_command(iget_fastqs.cmd, name="iget-fastqs")
irods.add_command(iget_cellranger.cmd, name="iget-cellranger")
irods.add_command(imeta_report.cmd, name="imeta-report")
irods.add_command(lsf.cmd, name="lsf")


@cli.group()
def scrna():
    """Commands for single-cell RNA-seq tools."""
    pass


scrna.add_command(cellbender.cmd, name="cellbender")
scrna.add_command(scanpy.cmd, name="scanpy")
scrna.add_command(merge_h5ad.cmd, name="merge-h5ad")
scrna.add_command(qc_basic.cmd, name="qc-basic")


if __name__ == "__main__":
    cli()
