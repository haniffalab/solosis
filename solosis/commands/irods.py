import click


@click.command(name="command-two")
@click.argument("filename", type=click.Path(exists=True))
def cmd(filename):
    """Read a file and print its contents."""
    with open(filename, "r") as f:
        content = f.read()
    click.echo(content)
