import getpass
import logging
import sys
import uuid
from datetime import datetime
from pathlib import Path

import click

LOG_DIR = Path.home() / ".solosis"
LOG_DIR.mkdir(exist_ok=True)

HISTORY_FILE = LOG_DIR / "history.log"

logger = logging.getLogger("solosis")
logger.setLevel(logging.INFO)


def log_history(uid: str):
    """Append command execution details to the history file."""
    user = getpass.getuser()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    command = " ".join(sys.argv)
    with open(HISTORY_FILE, "a") as f:
        f.write(f"{timestamp},{user},{uid},{command}\n")


def setup_logging():
    """Set up logging for the application."""
    execution_uid = str(uuid.uuid4())
    command_log_dir = LOG_DIR / execution_uid
    command_log_dir.mkdir(exist_ok=True)

    log_filename = command_log_dir / "output.log"
    error_filename = command_log_dir / "error.log"

    file_handler = logging.FileHandler(log_filename)
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    )
    file_handler.setLevel(logging.INFO)

    error_handler = logging.FileHandler(error_filename)
    error_handler.setFormatter(
        logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    )
    error_handler.setLevel(logging.ERROR)

    if not logger.handlers:
        logger.addHandler(file_handler)
        logger.addHandler(error_handler)

    log_history(execution_uid)

    return logger, execution_uid


def secho(message, type="info", bold=False):
    """Log a message with a specific type and color."""
    colors = {
        "info": "blue",  # Info messages will be blue
        "debug": "purple",  # Debug messages will be purple
        "error": "red",  # Error messages will be red
        "warn": "yellow",  # Warning messages will be yellow
        "success": "green",  # Success messages will be green
        "progress": "white",  # Progress messages will be white
        "action": "cyan",  # Action messages will be cyan
    }

    color = colors.get(type, "blue")
    click.echo(click.style(f"{type.capitalize()}: ", fg=color, bold=bold) + message)
