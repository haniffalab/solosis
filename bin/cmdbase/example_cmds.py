#!/usr/bin/env python3

# Your imports
import random
import click
import os
import subprocess

# Import vars
SHELL_SCRIPT_BASE =  os.environ['SHELL_SCRIPT_BASE']

# cmd name
@click.command("pull-fastqs")

# cmd options
@click.option('--samplefile', required=True, help="Sample file text file")

def fn():
    pass