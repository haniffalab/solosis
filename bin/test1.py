#!/usr/bin/env python3
import click
from cmdbase import pipeline


@click.group()
def cli():
    pass


@cli.group()
def test():
    pass


test.add_command(pipeline.irods.download_processed)

if __name__ == "__main__":
    cli()
