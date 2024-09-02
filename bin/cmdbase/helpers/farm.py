#!/usr/bin/env python3

import click
import functools


def farm(function):
    function = click.option('--mem')(function)
    function = click.option('--bar')(function)
    function = click.option('--foo')(function)
    return function


"""
def farm(func):
    @click.option("--mem")
    @click.option("--ncores")
    @click.option("--nprocs")
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

"""
