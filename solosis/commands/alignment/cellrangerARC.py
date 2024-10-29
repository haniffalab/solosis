import os
import subprocess

import click


@click.command("cellrangerARC")
@click.option("--samplefile", required=True, help="Sample file text file")
@click.option("--libraries", required=True, help="libraries file CSV")
# @click.option("--includebam", is_flag=True, default=False, help="Include BAM files",)
def cmd(samplefile, libraries):  ##will need to add 'includebam'
    """
    CellrangerARC aligns GEX & ATAC seq reads... \n
    --------------------------------- \n
    Cell RangerARC (2.0.2) Software suite designed for analysing & interpreting scRNA seq data, including multi-omics data.

    """
    shell_cellrangerARC_script = os.path.join(
        os.getcwd(),
        "bin/aligners/cellrangerARC/submit.sh",
    )

    # Pass the includebam flag as an argument to the bash script
    #    includebam = str(includebam * 1)
    #    includebam_str = "1" if includebam else "0"
    result_CRA = subprocess.run(
        [
            shell_cellrangerARC_script,
            samplefile,
            libraries,
        ],  # will need to add 'includebam'
        capture_output=True,
        text=True,
    )
    click.echo(result_CRA.stdout)
