import csv
import os
import re
from datetime import datetime

import click


def log_command(ctx):
    username = get_username()
    command_path = " ".join(ctx.command_path.split())
    command_args = " ".join(ctx.args)
    command_params = [
        f"--{key} {value}" for key, value in ctx.params.items() if value is not None
    ]

    # Determine the log file path
    log_dir = os.getenv("TEAM_LOGS_DIR", os.getcwd())
    log_file = os.path.join(log_dir, "history.csv")

    fieldnames = [
        "timestamp",
        "execution_id",
        "username",
        "solosis_version",
        "command_path",
        "command_args",
        "command_params",
    ]

    # Open file and append new entry
    with open(log_file, mode="a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if os.stat(log_file).st_size == 0:
            writer.writeheader()
        writer.writerow(
            {
                "timestamp": datetime.now().isoformat(),
                "execution_id": ctx.obj["execution_id"],
                "username": username,
                "solosis_version": ctx.obj["version"],
                "command_path": command_path,
                "command_args": command_args,
                "command_params": command_params,
            }
        )


def get_username():
    return os.getenv("USER") or os.getenv("USERNAME") or "unknown_user"


def echo_message(message, type="info", bold=False):
    """
    Log a message with a specific type and color.

    type: 'info', 'debug', 'error', 'warn'
    bold: Set to True to make the message bold
    """

    # Define the color for each message type
    colors = {
        "info": "blue",  # Info messages will be blue
        "debug": "purple",  # Debug messages will be purple
        "error": "red",  # Error messages will be red
        "warn": "yellow",  # Warning messages will be yellow
        "success": "green",  # Success messages will be green
        "progress": "white",  # Progress messages will be white
        "action": "cyan",  # Action messages will be cyan
    }

    # Default to 'info' type and blue color if an unrecognized type is passed
    color = colors.get(type, "blue")

    # Prefix with message type (e.g., [info], [error], etc.)
    prefix = f"[{type}] "

    # Print the styled message
    click.echo(
        click.style(
            prefix + message,
            fg=color,  # Use the appropriate color
            bold=bold,  # Make bold if specified
        )
    )


def echo_lsf_submission_message(job_stdout):
    """
    Log a standardized success message for LSF job submission.

    job_stdout: The standard output message returned by the LSF submission command.
    """
    match = re.search(r"Job <(\d+)> is submitted to queue <(\w+)>", job_stdout)
    if match:
        job_id, queue = match.groups()
        echo_message(
            f"LSF Job ID {click.style(job_id, bold=True, underline=True)} submitted to '{queue}' queue.",
            "success",
        )
    else:
        echo_message(f"LSF job submitted successfully:\n{job_stdout}", "success")

    echo_message("Use `bjobs` to monitor job completion.", "info")
    echo_message("View job logs at $HOME/logs.", "info")
