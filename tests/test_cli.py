import click
from click.testing import CliRunner

from solosis.cli import cli


def test_version():
    runner = CliRunner()
    result = runner.invoke(cli, ["--version"])
    assert result.exit_code == 0
    assert "version 0.2.3" in result.output


def test_help():
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "Show this message and exit" in result.output


def test_cellranger_count():
    runner = CliRunner()
    result = runner.invoke(cli, ["alignment", "cellranger-count", "--help"])
    assert result.exit_code == 0
    assert "Show this message and exit" in result.output


def test_cellranger_arc():
    runner = CliRunner()
    result = runner.invoke(cli, ["alignment", "cellranger-arc", "--help"])
    assert result.exit_code == 0
    assert "Show this message and exit" in result.output
