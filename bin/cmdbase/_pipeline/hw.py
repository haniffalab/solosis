#!/usr/bin/env python3

import click


@click.command("test_import")
def test_import():
    print("Hello World")
    return 0
