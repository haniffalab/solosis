import os
import subprocess
import sys
import time

import click

from solosis.utils import echo_message


def spinner():
    """Generator for spinner animation in the terminal."""
    spinner_frames = ["|", "/", "-", "\\"]
    while True:
        for frame in spinner_frames:
            yield frame


@click.command("filecount")
# @click.option("--workspace", type=str, required=True, help="Name of the workspace to check disk usage.")
def cmd():
    """
    Check disk usage for a specified workspace.

    This command retrieves the disk usage for a given workspace directory
    across NFS, Lustre, or warehouse storage systems.
    """
    # Print an introductory message
    echo_message(
        f"Launching: {click.style('filecount', bold=True, underline=True)}",
        "info",
    )

    # Ensure the base directory exists
    # if not os.path.isdir(team_workspace_dir):
    #    echo_message(
    #        f"Workspace directory '{team_workspace_dir}' does not exist.",
    #        "error",
    #    )
    #    return

    # Path to the Cell Ranger submission script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    filecount_submit_script = os.path.abspath(
        os.path.join(script_dir, "../../../bin/utilities/filecount/submit.sh")
    )
    # Construct the command with optional BAM flag
    cmd = [filecount_submit_script]

    # Create the spinner generator
    spin = spinner()

    try:
        with subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        ) as process:
            # While the command runs, show the spinner animation
            while True:
                # Check if the process has finished
                retcode = process.poll()
                if retcode is not None:  # Process has finished
                    break
                sys.stdout.write("\r" + next(spin))  # Overwrite the spinner
                sys.stdout.flush()  # Force output to the terminal
                time.sleep(0.1)  # Delay between spinner updates

            # Capture the output
            stdout, stderr = process.communicate()
            if process.returncode != 0:
                echo_message(
                    f"error during execution: {stderr}",
                    "warn",
                )
            else:
                echo_message(
                    f"\n{stdout.strip()}",
                    "progress",
                )

    except subprocess.CalledProcessError as e:
        echo_message(
            f"Error while calculating file count: {e.stderr.strip()}",
            "error",
        )


if __name__ == "__main__":
    cmd()
