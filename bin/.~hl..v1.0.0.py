#!/usr/bin/env python
#
#
import click
import subprocess
@click.group()
def irods():
    pass

@click.command()
def listfiles():
    result = subprocess.run(['ls'], capture_output=True, text=True)

irods.add_command(listfiles)

if __name__ == "__main__":
    irods()