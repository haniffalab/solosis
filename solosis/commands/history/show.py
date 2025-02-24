import os
from pathlib import Path

import click
from tabulate import tabulate

from solosis.utils.logging_utils import secho

FASTQ_EXTENSIONS = [".fastq", ".fastq.gz"]


@click.command("show")
@click.option(
    "--lines", "-n", default=10, help="Number of recent history entries to show."
)
def cmd(lines):
    """Show command execution history"""
    ctx = click.get_current_context()
    secho(
        f"Starting Process: {click.style(ctx.command.name, bold=True, underline=True)}",
        "info",
    )

    history_file = Path(os.getenv("SOLOSIS_LOG_DIR")) / "history.log"

    if not history_file.exists():
        secho("No history found.", type="error")
        return

    with open(history_file, "r") as f:
        lines_to_show = f.readlines()[-lines:]  # Get last `n` lines

    # Prepare data for the table
    table_data = []
    for entry in lines_to_show:
        timestamp, user, uid, command = entry.strip().split(",", 3)
        commands = Path(command.split("cli.py ")[-1])
        table_data.append(
            [
                timestamp,
                uid,
                commands,
            ]
        )

    # Define table headers
    headers = ["Timestamp", "UID", "Command"]

    # Output the history as a table
    table = tabulate(table_data, headers=headers, tablefmt="plain", stralign="left")
    click.echo(table)


if __name__ == "__main__":
    cmd()
