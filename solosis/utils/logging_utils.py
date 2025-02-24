import getpass
import logging
import os
import sys
import uuid
from datetime import datetime
from pathlib import Path

import click

logger = logging.getLogger("solosis")
logger.setLevel(logging.INFO)


def log_history(uid: str):
    """Append command execution details to the history file."""
    history_file = Path(os.getenv("SOLOSIS_LOG_DIR")) / "history.log"
    user = getpass.getuser()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    command = " ".join(sys.argv)
    with open(history_file, "a") as f:
        f.write(f"{timestamp},{user},{uid},{command}\n")


def setup_logging():
    """Set up logging for the application."""
    log_dir = Path(Path.home() / ".solosis")
    try:
        os.makedirs(log_dir, exist_ok=True)
        os.environ["SOLOSIS_LOG_DIR"] = str(log_dir)
    except OSError as e:
        secho(f"Failed to create log directory '{log_dir}': {e}", "error")
        raise click.Abort()

    execution_uid = str(uuid.uuid4())
    command_log_dir = log_dir / execution_uid
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
    click.echo(
        click.style(f"{type.capitalize()}: ", fg=color, bold=bold) + f"{message}"
    )
