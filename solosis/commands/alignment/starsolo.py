import os
import subprocess

import click


@click.command("starsolo")
@click.option("--samplefile", required=True, help="Sample file text file")
def cmd(samplefile):
    """
    STARsolo aligns sc-rna seq reads...
    --------------------------------- \n
    STARsolo (2.7.11b) Aligner processes scRNA seq data to generate GEX matrices & identify
    cell-specific transcripts.

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
