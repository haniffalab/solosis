import os
import subprocess

import click


@click.command("cellranger")
@click.option("--samplefile", required=True, help="Sample file text file")
@click.option(
    "--includebam",
    is_flag=True,
    default=False,
    help="Include BAM files (removes --no-bam from cellranger)",
)
def cmd(samplefile, includebam):
    """
    Cellranger aligns sc-rna seq reads... \n
    --------------------------------- \n
    Cellranger (7.2.0.) Sample demultiplexing, barcode processing, single cell 3' & 5' gene counting,
    V(D)J transcript sequence assembly.

    """
    shell_cellranger_script = os.path.join(
        os.getcwd(),
        "bin/aligners/cellranger/submit.sh",
    )

    # Pass the includebam flag as an argument to the bash script
    includebam = str(includebam * 1)
    includebam_str = "1" if includebam else "0"
    result_CR = subprocess.run(
        [shell_cellranger_script, samplefile, includebam],
        capture_output=True,
        text=True,
    )
    click.echo(result_CR.stdout)
