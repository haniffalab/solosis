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

        # Dictionary to store each process line and its current status
        lines = {}

        # Process stdout in real-time
        for line in process.stdout:
            timestamp = datetime.now().strftime("%H:%M:%S")
            line = line.strip()

            # Check if this line is being updated (e.g., by checking if it was previously printed)
            if line not in lines:
                lines[line] = False  # Mark it as a new line to be printed

            # If a line is marked as updated, overwrite it
            if lines[line]:
                sys.stdout.write(f"\r[{timestamp}] {line}")
                sys.stdout.flush()
            else:
                sys.stdout.write(f"[{timestamp}] {line}\n")
                sys.stdout.flush()
                lines[line]

        for line in process.stderr:
            logger.error(f"{line.strip()}")

        process.wait()
        if process.returncode != 0:
            logger.error(f"Error during execution. Return code: {process.returncode}")
        else:
            logger.info("Process completed successfully.")
    except Exception as e:
        logger.error(f"Error executing command: {e}")
