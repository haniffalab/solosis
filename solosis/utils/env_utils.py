import getpass
import os
import subprocess

import click

from solosis.utils.state import logger


def validate_env():
    """Ensure all required environment variables are set and sample directory exists."""
    required_vars = ["TEAM_DATA_DIR", "LSB_DEFAULT_USERGROUP"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        logger.error(
            f"Missing environment variables: {', '.join(missing_vars)}. Please export them before running Solosis."
        )
        raise click.Abort()

    samples_dir = os.path.join(os.getenv("TEAM_DATA_DIR"), "samples")
    try:
        os.makedirs(samples_dir, exist_ok=True)
        os.environ["TEAM_SAMPLES_DIR"] = samples_dir
    except OSError as e:
        logger.error(f"Failed to create sample data directory '{samples_dir}': {e}")
        raise click.Abort()

    tmp_dir = os.path.join(os.getenv("TEAM_DATA_DIR"), "tmp")
    try:
        os.makedirs(tmp_dir, exist_ok=True)
        os.environ["TEAM_TMP_DIR"] = tmp_dir
    except OSError as e:
        logger.error(f"Failed to create sample data directory '{samples_dir}': {e}")
        raise click.Abort()


def irods_auth(timeout=5):
    """Validate irods authentication."""
    try:
        logger.info("Checking iRODS authentication status...")
        result = subprocess.run(
            ["iget", "dummy"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
            timeout=timeout,
        )

        if result.returncode != 0:
            # Check if the response indicates that the user is authenticated
            if "USER_INPUT_PATH_ERR" in result.stderr:
                logger.info("iRODS authenticated")
                return True

            logger.error(f"iRODS command failed with return code {result.returncode}")
            logger.info(f"Standard Output:\n{result.stdout}")
            logger.error(f"Standard Error:\n{result.stderr}")

    except FileNotFoundError:
        logger.error(
            "iRODS commands not found. Ensure iRODS is installed and the module is loaded."
        )
        return False

    except Exception as e:
        # Assuming error is a timeout, indicating user in not authenticated.
        password = getpass.getpass("Enter iRODS Password: ")
        subprocess.run(["stty", "sane"])  # Needed to reset terminal state
        process = subprocess.Popen(
            ["iinit"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        process.communicate(input=password + "\n")
        if process.returncode == 0:
            logger.info(f"iRODS authenticated")
            return True
        else:
            logger.error(f"iRODS initialization failed")

    return False
