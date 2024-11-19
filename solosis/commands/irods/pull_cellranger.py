import os
import subprocess

import click


@click.command("pull-processed")
@click.option("--samplefile", required=True, help="Sample file text file")
@click.option(
    "--retainbam",
    default=False,
    is_flag=True,
    required=False,
    help="Download alignment bam file",
)
@click.option(
    "--overwrite",
    default=False,
    is_flag=True,
    required=False,
    help="Overwrite existing folder contents",
)
def cmd(samplefile, retainbam, overwrite):
    """
    Downloads processed iRODS data or any folder from iRODS
    -----------------------

    Example: /lustre/scratch126/cellgen/team298/soft/bin/examples/irods_download.txt
    Input file should have 3 mandatory columns:
    1st column: sanger_id, 2nd column: sample_name, LAST column: irods path

    """
    print("Using irods to download data")
    print("If you have a large set of files, this command will take a while to run")

    shell_cellranger_script = os.path.join(
        os.getcwd(),
        "bin/irods/pull-cellranger/submit.sh",
    )
    overwrite = str(overwrite * 1)
    retainbam = str(retainbam * 1)
    result = subprocess.run(
        [shell_cellranger_script, samplefile, retainbam, overwrite],
        capture_output=True,
        text=True,
    )
    click.echo(result.stdout)
    click.echo(result.stderr)
