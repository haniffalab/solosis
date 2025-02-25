import csv
import logging
import os
from pathlib import Path

import click

from solosis.utils.logging_utils import debug
from solosis.utils.state import logger


@debug
@click.command("uid")
@click.argument("uid")
def cmd(uid, debug):
    """Show detailed information about a specific execution using UID."""
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

    matching_entry = None
    with open(history_file, "r") as f:
        reader = csv.reader(f)
        for index, entry in enumerate(reader):
            if len(entry) >= 4 and entry[3] == uid:  # Check the 4th column (index 3)
                matching_entry = entry
                break

    if not matching_entry:
        logger.error(f"No log entry found for UID: {uid}")
        raise click.Abort()

    if len(matching_entry) < 5:
        logger.error("Malformed log entry for UID: %s", uid)
        raise click.Abort()

    timestamp, user, version, uid, command = matching_entry
    log_dir = Path(os.getenv("SOLOSIS_LOG_DIR")) / uid
    logger.info(f"{click.style('Execution UID', bold=True)}: {uid}")
    logger.info(f"{click.style('Timestamp', bold=True)}: {timestamp}")
    logger.info(f"{click.style('User', bold=True)}: {user}")
    logger.info(f"{click.style('Command', bold=True)}: {command}")
    logger.info(f"{click.style('Logs', bold=True)}: {log_dir}")
    if log_dir.exists():
        for item in log_dir.iterdir():
            logger.info(f"├── {item}")
    else:
        logger.warning(f"Log directory {log_dir} does not exist.")
