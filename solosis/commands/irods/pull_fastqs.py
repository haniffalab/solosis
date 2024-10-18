import os
import subprocess

import click


@click.command("pull-fastqs")
@click.option("--samplefile", required=True, help="Sample file text file")
def cmd(samplefile):
    """
    Downloading fastqs from iRODS... 
    Requires a sample file.
    """
    print("Using iRODS to download data")
    print("If you have a large set of files, this command will take a while to run")

    shell_script_fq = os.path.join(
        os.getcwd(),
        "/software/cellgen/team298/shared/solosis/bin/irods/pull-fastqs/submit.sh",
    )

    result_fq = subprocess.run(
        [shell_script_fq, samplefile], capture_output=True, text=True
    )
    click.echo(result_fq.stdout)
    click.echo(result_fq.stderr)
