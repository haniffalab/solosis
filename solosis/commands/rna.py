import click


@click.command(name="command-one")
@click.option("--name", default="World", help="Name to greet.")
def cmd(name):
    """Greet someone by name."""
    click.echo(f"Hello, {name}!")
