import os
import subprocess

import click


@click.command("starsolo")
@click.option("--samplefile", required=True, help="Sample file text file")
def cmd(samplefile):
    """
    STARsolo aligns sc-rna seq reads...
    --------------------------------- \n
        [ S T A R S O L O ]

    STARsolo ...
    Version:2.7.11b

    sample_ID: list of samples, CSV file format needed and header as 'samples'
    ---------------------------------
    """
    shell_starsolo_script = os.path.join(
        os.getcwd(),
        "/software/cellgen/team298/shared/solosis/bin/aligners/starsolo/submit.sh",
    )
    # can we change script base to sc-voyage dir
    result_STAR = subprocess.run(
        [shell_starsolo_script, samplefile], capture_output=True, text=True
    )
    click.echo(result_STAR.stdout)
