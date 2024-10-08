import click


@click.command("pull-fastqs")
@click.option("--samplefile", required=True, help="Sample file text file")
def cmd(samplefile):
    """
    Downloads processed irods data or any folder from irods
    and saves it to $HL_IRODS_DOWNLOAD. This is set when you load module
    Requires a sample file.
    """
    print("Using irods to download data")
    print("If you have a large set of files, this command will take a while to run")
    shell_script_fq = os.path.join(SHELL_SCRIPT_BASE, "irods..fastqs")
    result_fq = subprocess.run(
        [shell_script_fq, samplefile], capture_output=True, text=True
    )
    click.echo(result_fq.stdout)
    click.echo(result_fq.stderr)
