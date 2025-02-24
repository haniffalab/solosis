import csv
import os
from pathlib import Path

import click

from solosis.utils.logging_utils import secho


@click.command("uid")
@click.argument("uid")
@click.pass_context
def cmd(uid):
    """Show detailed information about a specific execution using UID."""
    ctx = click.get_current_context()
    secho(
        f"Starting Process: {click.style(ctx.command.name, bold=True, underline=True)}",
        "info",
    )
    secho(f"Fetching details for UID: {uid}", "info")

    history_file = Path(os.getenv("SOLOSIS_LOG_DIR")) / "history.log"

    if not history_file.exists():
        secho("No history found.", type="error")
        return

    # Search for the UID efficiently using the CSV module
    matching_entries = []
    with open(history_file, "r") as f:
        reader = csv.reader(f)
        matching_entries = [
            entry for entry in reader if len(entry) >= 3 and entry[2] == uid
        ]

    if not matching_entries:
        secho(f"No entries found for UID: {uid}", type="error")
        return

    # Prepare and print the details for each entry
    for entry in matching_entries:
        timestamp, user, log_uid, command = entry[0], entry[1], entry[2], entry[3]

        # Output entry details
        secho(f" ", "info")
        secho(
            f"{click.style('Timestamp', bold=True, underline=True)}: {timestamp}",
            "info",
        )
        secho(f"{click.style('User', bold=True, underline=True)}: {user}", "info")
        secho(f"{click.style('UID', bold=True, underline=True)}: {log_uid}", "info")
        secho(f"{click.style('Command', bold=True, underline=True)}: {command}", "info")
        secho(f" ", "info")

        # Location of the log directory for this UID
        log_dir = Path(os.getenv("SOLOSIS_LOG_DIR")) / log_uid
        secho(
            f"{click.style('Log directory', bold=True, underline=True)}: {log_dir}",
            "info",
        )
        if log_dir.exists():
            # Listing contents of the log directory
            secho(
                f"{click.style('Contents of log directory', bold=True, underline=True)}:",
                "info",
            )
            for item in log_dir.iterdir():
                secho(f"  {item}", "info")
        else:
            secho(f"Log directory {log_dir} does not exist.", "error")
