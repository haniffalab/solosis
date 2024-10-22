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

    Example: /lustre/scratch126/cellgen/team298/soft/bin/examples/irods_download.txt \n
    Input file should have 3 mandatory columns \n
    1st column: sanger_id \n
    2nd column: sample_name \n
    LAST column: irods path \n

    :params samplefile: Input file (.txt)
    :params retainbam: Inldue BAM files in download
    :params overwrite: Overwrite existing download
    ----------------------

    """
    print("Using irods to download data")
    print("If you have a large set of files, this command will take a while to run")

    shell_cellranger_script = os.path.join(
        os.getcwd(),
        "/software/cellgen/team298/shared/solosis/bin/irods/pull-cellranger/submit.sh",
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
