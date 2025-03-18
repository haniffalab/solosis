import subprocess
import sys
from collections import deque
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

        # Create a deque to hold the last 5 lines of output
        recent_lines = deque(maxlen=5)

        # Print 5 empty lines to start
        for _ in range(5):
            print()

        # Process stdout in real-time
        for line in process.stdout:
            timestamp = datetime.now().strftime("%H:%M:%S")
            recent_lines.append(
                f"[{timestamp}] {line.strip()}"
            )  # Add the new line with timestamp

            # Move the cursor up by 5 lines
            sys.stdout.write("\033[F" * 5)

            # Print the last 5 lines (or fewer, depending on the deque's size)
            for recent_line in recent_lines:
                print(recent_line)

            sys.stdout.flush()  # Ensure immediate update

        for line in process.stderr:
            logger.error(f"{line.strip()}")

        process.wait()
        if process.returncode != 0:
            logger.error(f"Error during execution. Return code: {process.returncode}")
        else:
            logger.info("Process completed successfully.")
    except Exception as e:
        logger.error(f"Error executing command: {e}")
