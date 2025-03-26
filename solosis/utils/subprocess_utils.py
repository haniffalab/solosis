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
        logger.debug(f"Starting subprocess for: {command}")
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )

        # Process stdout in real-time
        lines = 7
        recent_lines = deque([""] * lines, maxlen=lines)
        for _ in range(lines):
            print()
        for line in process.stdout:
            timestamp = datetime.now().strftime("%H:%M:%S")
            recent_lines.append(f"[{timestamp}] {line.strip()}")
            sys.stdout.write("\033[F" * lines)
            for recent_line in recent_lines:
                print(recent_line)
            sys.stdout.flush()

        for line in process.stderr:
            logger.error(f"{line.strip()}")

        process.wait()
        if process.returncode != 0:
            logger.error(f"Error during execution. Return code: {process.returncode}")
        else:
            logger.debug("Subprocess completed successfully")
    except Exception as e:
        logger.error(f"Error executing command: {e}")
