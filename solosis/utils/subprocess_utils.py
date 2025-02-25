import subprocess

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

        for line in process.stdout:
            logger.info(f"{line.strip()}")

        for line in process.stderr:
            logger.error(f"{line.strip()}")

        process.wait()
        if process.returncode != 0:
            logger.error(f"Error during execution. Return code: {process.returncode}")
        else:
            logger.info("Process completed successfully.")
    except Exception as e:
        logger.error(f"Error executing command: {e}")
