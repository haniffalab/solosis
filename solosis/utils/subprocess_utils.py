import subprocess
import sys
from datetime import datetime

from solosis.utils.state import logger


def popen(
    command: str,
):
    """Submit an LSF job array where each job runs a command from a file."""
    try:
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,  # Line buffering
        )

        # Process stdout in real-time
        for line in process.stdout:
            timestamp = datetime.now().strftime("%H:%M:%S")
            sys.stdout.write(
                f"\r[{timestamp}] {line.strip()}"
            )  # Use \r to overwrite the line
            sys.stdout.flush()

        for line in process.stderr:
            logger.error(f"{line.strip()}")

        process.wait()
        if process.returncode != 0:
            logger.error(f"Error during execution. Return code: {process.returncode}")
        else:
            logger.info("Process completed successfully.")
    except Exception as e:
        logger.error(f"Error executing command: {e}")
