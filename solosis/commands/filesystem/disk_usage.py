import os
import subprocess

import click

from solosis.utils import echo_message


@click.command("disk-usage")
# @click.option("--workspace", type=str, required=True, help="Name of the workspace to check disk usage.")
def cmd():
    """
    Check disk usage for a specified workspace.

    This command retrieves the disk usage for a given workspace directory
    across NFS, Lustre, or warehouse storage systems.
    """
    ctx = click.get_current_context()
    echo_message(
        f"Starting Process: {click.style(ctx.command.name, bold=True, underline=True)}",
        "info",
    )

    # not sure this is necessary
    # Get the base directory for the team workspaces
    team_workspace_dir = os.getenv(
        "TEAM_WORKSPACE_DIR", "/lustre/scratch126/cellgen/team298/workspaces"
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
    diskusage_submit_script = os.path.abspath(
        os.path.join(script_dir, "../../../bin/filesystem/disk-usage/submit.sh")
    )
    # Construct the command with optional BAM flag
    cmd = [diskusage_submit_script]

    ####this may not be relevant now..
    # if not os.path.exists(workspace_path):
    #    echo_message(
    #        f"Workspace '{workspace}' does not exist at path '{workspace_path}'.",
    #        "error",
    #    )
    #    return

    # Run the cmd to calculate disk usage
    try:
        echo_message(f"Calculating disk usage for team298 ...", "progress")
        result = subprocess.run(
            cmd,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        echo_message(f"\n{result.stdout.strip()}", "progress")
    except subprocess.CalledProcessError as e:
        echo_message(
            f"Error while calculating disk usage: {e.stderr.strip()}",
            "error",
        )


if __name__ == "__main__":
    cmd()
