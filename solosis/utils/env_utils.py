import getpass
import os
import subprocess

import click

from solosis.utils.logging_utils import secho


def validate_env():
    """Ensure all required environment variables are set and sample directory exists."""
    required_vars = ["TEAM_DATA_DIR", "LSB_DEFAULT_USERGROUP"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        secho(
            f"Missing environment variables: {', '.join(missing_vars)}. Please export them before running Solosis.",
            "error",
        )
        raise click.Abort()

    samples_dir = os.path.join(os.getenv("TEAM_DATA_DIR"), "samples")
    try:
        os.makedirs(samples_dir, exist_ok=True)
        os.environ["TEAM_SAMPLES_DIR"] = samples_dir
    except OSError as e:
        secho(f"Failed to create sample data directory '{samples_dir}': {e}", "error")
        raise click.Abort()

    tmp_dir = os.path.join(os.getenv("TEAM_DATA_DIR"), "tmp")
    try:
        os.makedirs(tmp_dir, exist_ok=True)
        os.environ["TEAM_TMP_DIR"] = tmp_dir
    except OSError as e:
        secho(f"Failed to create sample data directory '{samples_dir}': {e}", "error")
        raise click.Abort()


def irods_auth(timeout=5):
    """Validate irods authentication."""
    try:
        secho("Checking iRODS authentication status...", "info")
        result = subprocess.run(
            ["iget", "dummy"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
            timeout=timeout,
        )

        # Capture errors from stderr even if the command "succeeded" but returned errors
        if result.returncode != 0:
            # Check if the error indicates that the user is authenticated
            if "USER_INPUT_PATH_ERR" in result.stderr:
                secho("iRODS authenticated.", "success")
                return True

            secho(f"iget command failed with return code {result.returncode}", "error")
            secho(f"Standard Output:\n{result.stdout}", "info")
            secho(f"Standard Error:\n{result.stderr}", "error")

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
            secho(f"iRODS authenticated...", "success")
            return True
        else:
            secho(f"iRODS initialization failed", "error")

    return False
