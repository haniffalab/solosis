import click


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
        "action": "cyan",  # action messages will be cyan
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
    echo_message(f"LSF job submitted successfully:\n{job_stdout}", "success")
    echo_message("Use `bjobs` to monitor job completion.", "info")
    echo_message("View job success at $HOME/logs.", "info")
