import os

import click
from click.testing import CliRunner

from solosis.cli import cli

# responding to error message ("missing environmnet variables LSB_DEFAULT_USERGROUP and TEAM_DATA_DIR")
os.environ["LSB_DEFAULT_USERGROUP"] = "team298"
os.environ["TEAM_DATA_DIR"] = "/lustre/scratch126/cellgen/team298/data"


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
    assert result.exit_code == 0
    assert "Show this message and exit" in result.output


def test_cellranger_arc_count():
    runner = CliRunner()
    result = runner.invoke(cli, ["alignment", "cellranger-arc-count", "--help"])
    assert result.exit_code == 0
    assert "Show this message and exit" in result.output


def test_imeta_report():
    runner = CliRunner()
    result = runner.invoke(cli, ["irods", "imeta-report", "--help"])
    assert result.exit_code == 0
    assert "Show this message and exit" in result.output


def test_iget_cellranger():
    runner = CliRunner()
    result = runner.invoke(cli, ["irods", "iget-cellranger", "--help"])
    assert result.exit_code == 0
    assert "Show this message and exit" in result.output


def test_iget_fastqs():
    runner = CliRunner()
    result = runner.invoke(cli, ["irods", "iget-fastq", "--help"])
    assert result.exit_code == 0
    assert "Show this message and exit" in result.output
