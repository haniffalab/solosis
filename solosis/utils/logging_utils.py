import getpass
import logging
import os
import sys
import uuid
from datetime import datetime
from pathlib import Path

import click
from colorama import Fore, Style

try:
    import tomllib
except ImportError:
    import tomli as tomllib

logger = logging.getLogger("solosis")
logger.setLevel(logging.INFO)
execution_uid = None


def debug(func):
    """Decorator to add a --debug flag to commands."""

    @click.option("--debug", is_flag=True, help="Enable debug mode")
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper


def log(function):
    """Decorator that logs execution details."""

    def wrapper(*args, **kwargs):
        global execution_uid
        if execution_uid:
            history_file = Path(os.getenv("SOLOSIS_LOG_DIR")) / "history.log"
            user = getpass.getuser()
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            version = get_version()
            command = " ".join(sys.argv)

            with open(history_file, "a") as f:
                f.write(f"{timestamp},{user},{version},{execution_uid},{command}\n")

        return function(*args, **kwargs)

    return wrapper


def get_version():
    try:
        pyproject_path = os.path.join(
            os.path.dirname(__file__), "../../", "pyproject.toml"
        )
        with open(pyproject_path, "rb") as f:
            data = tomllib.load(f)
        return data.get("project", {}).get("version", "unknown")
    except Exception as e:
        logger.error(f"Error reading version from pyproject.toml: {e}")
        return "unknown"


def setup_logging():
    """Set up logging for the application."""
    global execution_uid
    log_dir = Path(Path.home() / ".solosis")
    try:
        os.makedirs(log_dir, exist_ok=True)
        os.environ["SOLOSIS_LOG_DIR"] = str(log_dir)
    except OSError as e:
        logger.error(f"Failed to create log directory '{log_dir}': {e}")
        raise click.Abort()

    execution_uid = str(uuid.uuid4())
    command_log_dir = log_dir / execution_uid
    command_log_dir.mkdir(exist_ok=True)

    log_filename = command_log_dir / "solosis_output.log"
    error_filename = command_log_dir / "solosis_error.log"

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

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(ColoredFormatter("%(levelname)s: %(message)s"))
    console_handler.setLevel(logging.DEBUG)
    logger.addHandler(console_handler)

    version = get_version()

    return logger, execution_uid, version


class ColoredFormatter(logging.Formatter):
    """Custom formatter to add colors to log level names."""

    LEVEL_COLORS = {
        "DEBUG": Fore.MAGENTA,
        "INFO": Fore.BLUE,
        "WARNING": Fore.YELLOW,
        "ERROR": Fore.RED,
        "CRITICAL": Fore.RED + Style.BRIGHT,
    }

    def format(self, record):
        levelname = record.levelname
        color = self.LEVEL_COLORS.get(levelname, Fore.WHITE)
        record.levelname = f"{color}{levelname}{Style.RESET_ALL}"
        return super().format(record)
