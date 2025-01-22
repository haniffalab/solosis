import click
from click.testing import CliRunner

from solosis.cli import cli


def test_version():
    runner = CliRunner()
    result = runner.invoke(cli, ["--version"])
    assert result.exit_code == 0
    assert "version 0.3.0" in result.output


def test_help():
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "Show this message and exit" in result.output


def test_cellranger_count():
    runner = CliRunner()
    result = runner.invoke(cli, ["alignment", "cellranger-count", "--help"])
    print(result.output)
    assert result.exit_code == 0
    assert "Show this message and exit" in result.output
