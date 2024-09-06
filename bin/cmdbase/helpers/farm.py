#!/usr/bin/env python3

import click


def farm(function):
    function = click.option("--mem")(function)
    function = click.option("--cores")(function)
    function = click.option("--time")(function)
    return function
