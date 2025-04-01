import logging
import os
import re
from datetime import datetime, timedelta
from pathlib import Path

import click

from solosis.utils.logging_utils import debug
from solosis.utils.state import logger

UUID_REGEX = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.IGNORECASE
)


@click.command("clear")
@click.option("--hours", "-h", default=168, help="Age of logs to clear in hours.")
@debug
def cmd(hours, debug):
    """Clear log entries and old log directories older than the specified number of hours."""
    if debug:
        logger.setLevel(logging.DEBUG)

    ctx = click.get_current_context()
    logger.debug(
        f"Starting command: {click.style(ctx.command.name, bold=True, underline=True)}"
    )

    log_dir = Path(os.getenv("SOLOSIS_LOG_DIR"))
    history_file = log_dir / "history.log"

    current_time = datetime.now()
    cutoff_time = current_time - timedelta(hours=hours)

    if not history_file.exists():
        logger.error(f"No history found")
        raise click.Abort()

    valid_entries = []
    with open(history_file, "r") as f:
        for entry in f:
            parts = entry.strip().split(",")
            if len(parts) < 5:
                logger.warning("Skipping malformed log entry: %s", entry.strip())
                continue

            timestamp_str = parts[0]
            try:
                timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                logger.warning(f"Skipping malformed timestamp: {timestamp_str}")
                continue

            if timestamp >= cutoff_time:
                valid_entries.append(entry)
            else:
                logger.debug(f"Removing log entry: {entry.strip()}")

    with open(history_file, "w") as f:
        f.writelines(valid_entries)

    for directory in log_dir.iterdir():
        if directory.is_dir() and UUID_REGEX.match(directory.name):
            try:
                dir_mtime = datetime.fromtimestamp(directory.stat().st_mtime)
                if dir_mtime < cutoff_time:
                    logger.debug(f"Deleting old log directory: {directory}")
                    for item in directory.iterdir():
                        item.unlink()
                    directory.rmdir()
            except Exception as e:
                logger.warning(f"Failed to remove {directory}: {e}")

    logger.info(f"Cleared logs and directories older than {hours} hours.")


if __name__ == "__main__":
    cmd()
