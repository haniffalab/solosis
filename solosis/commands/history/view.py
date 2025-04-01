import logging
import os
from pathlib import Path

import click
from tabulate import tabulate

from solosis.utils.logging_utils import debug
from solosis.utils.state import logger


@click.command("view")
@click.option(
    "--lines", "-n", default=10, help="Number of recent history entries to show."
)
@debug
def cmd(lines, debug):
    """Show command execution history"""
    if debug:
        logger.setLevel(logging.DEBUG)

    ctx = click.get_current_context()
    logger.debug(
        f"Starting command: {click.style(ctx.command.name, bold=True, underline=True)}"
    )

    history_file = Path(os.getenv("SOLOSIS_LOG_DIR")) / "history.log"
    if not history_file.exists():
        logger.error(f"No history found")
        raise click.Abort()

    with open(history_file, "r") as f:
        lines_to_show = f.readlines()[-lines:]

    table_data = []
    for entry in lines_to_show:
        parts = entry.strip().split(",")
        if len(parts) < 5:
            logger.warning("Malformed history entry: %s", entry.strip())
            continue

        timestamp, user, version, uid, command = parts[:5]
        commands = command.split(" ", 1)[-1]

        table_data.append(
            [
                timestamp,
                uid,
                commands,
            ]
        )

    headers = ["Timestamp", "UID", "Command"]
    table = tabulate(table_data, headers=headers, tablefmt="plain", stralign="left")
    logger.info(f"{lines} recent log entries:\n{table}")


if __name__ == "__main__":
    cmd()
