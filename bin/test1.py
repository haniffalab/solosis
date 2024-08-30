#!/software/cellgen/team298/shared/envs/hlb-conda/hl_minimal_v1.0.0/bin/python
import click
import os
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
