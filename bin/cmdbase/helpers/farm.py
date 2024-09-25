#!/usr/bin/env python3

import click


def farm(function):
    function = click.option("--mem", default = 50000, type = int,  help = "mem in MB")(function)
    function = click.option("--cores", default = 4, type = int, help = "# of cores")(function)
    function = click.option("--time", default = "12:00:00", help = "time for running")(function)
    function = click.option("--queue", default = "normal", help = "queue name")(function)
    return function
