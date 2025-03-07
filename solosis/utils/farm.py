import csv
import os
import re
import subprocess
import sys
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
    os.makedirs(log_dir, exist_ok=True)

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


## Functions supporting farm submission
def bash_submit(job_runner: str, **kwargs) -> None:
    """
    Runs a command. Command can be a bash command (du -hs ) or a script (test.sh)
    While running exports all kwargs as environment variables
    This can be reused to run any bash script in all the subcommands
    If the command needs to be submitted to farm use single_command or array_command
    """
    # env variables are set to
    for k, v in kwargs.items():
        kwargs[str(k)] = str(v)
    # Capture result
    result = subprocess.run(
        [job_runner], capture_output=True, text=True, env={**os.environ, **kwargs}
    )

    click.echo(result.stdout)
    click.echo(result.stderr)


def _single_command_bsub(command_to_exec, job_name, queue, time, cores, mem, **kwargs):
    """
    Run a single command on the farm.
    """
    # Script directory in the solosis package
    script_dir = os.path.dirname(os.path.abspath(__file__))
    print(script_dir)
    # codebase = os.path.join(script_dir, "..", "..", "..", "bin")
    job_runner = os.path.abspath(os.path.join(script_dir, "../bin/farm/single_job.sh"))
    if len(command_to_exec) == 0:
        echo_message("No command to execute", type="error")
        return

    # command_to_exec = " ".join(command_to_exec)
    bash_submit(
        job_runner,
        command_to_exec=command_to_exec,
        job_name=job_name,
        queue=queue,
        time=time,
        cores=cores,
        mem=mem,
    )


def irods_validation():
    """Run a command and handle specific output conditions."""
    command = [
        "iget",
        "/seq/illumina/runs/48/48297/cellranger/cellranger720_count_48297_58_rBCN14591738_GRCh38-2020-A/web_summary.html",
    ]

    try:
        # Run the command and capture stdout and stderr
        result = subprocess.run(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )

        # Check for the specific error in stderr
        if (
            "CAT_INVALID_AUTHENTICATION" in result.stderr
            or "-827000 CAT_INVALID_USER" in result.stderr
        ):
            echo_message(
                "run `iinit` before re-running this solosis command.",
                "error",
            )
            sys.exit(1)  # Exit with error status 1

        # If no error, command executed successfully
        echo_message("Command executed successfully.", "success")

    except FileNotFoundError:
        echo_message(
            "iRODS not loaded. please run `module load cellgen/irods` before re-running this solosis command.",
            "error",
        )
        sys.exit(1)


def validate_environment(required_vars):
    """
    Validates that all required environment variables are set.
    :param required_vars: List of required environment variable names.
    :raises click.Abort: If any required variable is not set.
    """
    for var in required_vars:
        if not os.getenv(var):
            echo_message(
                f"Environment variable '{var}' is not set. Please export it before running this tool.",
                "error",
            )
            raise click.Abort()
