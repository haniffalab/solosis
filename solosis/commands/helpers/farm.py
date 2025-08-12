#!/usr/bin/env python3

import click


def job_resources(function):
    function = click.option("--mem", default=50000, type=int, help="mem in MB")(
        function
    )
    function = click.option("--cores", default=4, type=int, help="# of cores")(function)
    function = click.option(
        "--time", default="12:00", type=str, help="time for running"
    )(function)
    function = click.option("--queue", default="normal", type=str, help="queue name")(
        function
    )
    function = click.option("--cpu", default="1", type=int, help="CPUs used")(function)

    return function
