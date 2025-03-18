import subprocess
import sys
from collections import deque

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
        )

        # Create a deque with a max length of 4 to keep the most recent 4 lines
        recent_lines = deque(maxlen=4)

        # Print initial message indicating the process is running
        sys.stdout.write("Process started...\n")
        sys.stdout.flush()

        for line in process.stdout:
            # Add the new line to the deque (it will automatically discard the oldest one if > 4 lines)
            recent_lines.append(line.strip())

            # Clear only the lines printed by this block (move cursor up by the number of lines in recent_lines)
            sys.stdout.write(
                "\033[F" * len(recent_lines)
            )  # Move cursor up by the number of lines

            # Print all the recent lines in the deque
            for recent_line in recent_lines:
                print(recent_line)

            sys.stdout.flush()

        print()  # Final print after all lines are done printing

        for line in process.stderr:
            logger.error(f"{line.strip()}")

        process.wait()
        if process.returncode != 0:
            logger.error(f"Error during execution. Return code: {process.returncode}")
        else:
            logger.info("Process completed successfully.")
    except Exception as e:
        logger.error(f"Error executing command: {e}")
