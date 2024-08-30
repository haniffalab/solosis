import random
import click


@click.command("cellbender")
@click.option('--total_droplets_included', required=True, help="total_droplets_included")
def cellbender(total_droplets_included, **kwargs):
    """
    Cellbender Removes droplets and ambient RNA from scRNA seq data. \n
    --------------------------------- \n
        [ C E L L B E N D E R]  

    Cellbender Removes droplets and ambient RNA from scRNA seq data.  
    Version:0.3.0.
   
    sample_ID: list of samples, CSV file format needed and header as 'samples'
    ---------------------------------
    """
    shell_cellbender_script=os.path.join(SHELL_SCRIPT_BASE,"test..submit_cellbender") #can we change script base to sc-voyage d>
    result_CB = subprocess.run([shell_cellbender_script, total_droplets_included], capture_output=True, text=True)
    click.echo(result_CB.stdout)

