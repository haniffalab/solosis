#!/usr/bin/env python3

import os

import click
import pandas as pd
from tabulate import tabulate


@click.command("history")
@click.option(
    "--last", required=False, help="Retrieve last n commands", default=10, type=int
)
@click.option(
    "--all",
    default=False,
    is_flag=True,
    required=False,
    help="Retrieve all history",
)
def history(last, all):
    CWD = os.environ["CWD"]
    hist_file = os.path.join(CWD, ".pap/") + "hist"
    if not os.path.exists(hist_file):
        click.echo("No history file present")
        return 0
    hist = pd.read_csv(hist_file, index_col=0)
    if all:
        print(tabulate(hist, headers="keys", tablefmt="plain"))
    else:
        print(tabulate(hist.tail(last), headers="keys", tablefmt="plain"))
    return 0
