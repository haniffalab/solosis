import os
import subprocess

import click


@click.command("cellrangerARC")
@click.option("--samplefile", required=True, help="Sample file text file")
@click.option("--libraries", required=True, help="libraries file CSV")
#@click.option("--includebam", is_flag=True, default=False, help="Include BAM files",)
def cmd(samplefile, libraries): ##will need to add 'includebam'
    """
    CellrangerARC aligns GEX & ATAC seq reads... \n
    --------------------------------- \n
        [ CELLRANGER ARC ]

    CellrangerARC sample demultiplexing... ADD MORE \n
    Version: 2.0.2

    samplefile: list of samples, CSV file format needed and header as 'samples'
    libraries: standard input for cellranger arc CSV file format
    ---------------------------------
    """
    shell_cellrangerARC_script = os.path.join(
        os.getcwd(), "/software/cellgen/team298/shared/solosis/bin/aligners/cellrangerARC/submit.sh"
    )

    # Pass the includebam flag as an argument to the bash script
#    includebam = str(includebam * 1)
#    includebam_str = "1" if includebam else "0"
    result_CRA = subprocess.run(
        [shell_cellrangerARC_script, samplefile, libraries], #will need to add 'includebam'
        capture_output=True,
        text=True,
    )
    click.echo(result_CRA.stdout)
