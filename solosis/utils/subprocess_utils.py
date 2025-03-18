import subprocess
import sys

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

        output_lines = []  # Store output lines for tracking

        for line in process.stdout:
            output_lines.append(line.strip())

            # Move the cursor up for each previous line
            for _ in range(len(output_lines)):
                sys.stdout.write("\033[F")  # Move cursor up

            # Clear the lines
            sys.stdout.write("\033[J")  # Clear from cursor to end of screen

            # Reprint the updated output
            for out_line in output_lines:
                print(out_line)

            sys.stdout.flush()  # Ensure immediate update

        print()

        for line in process.stderr:
            logger.error(f"{line.strip()}")

        process.wait()
        if process.returncode != 0:
            logger.error(f"Error during execution. Return code: {process.returncode}")
        else:
            logger.info("Process completed successfully.")
    except Exception as e:
        logger.error(f"Error executing command: {e}")
