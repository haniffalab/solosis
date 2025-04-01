import os

import click
from click.testing import CliRunner

from solosis.cli import cli

# responding to error message ("missing environmnet variables LSB_DEFAULT_USERGROUP and TEAM_DATA_DIR")
os.environ["LSB_DEFAULT_USERGROUP"] = "team298"
os.environ["TEAM_DATA_DIR"] = "/tmp/solosis"


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


## Tests for alignment commands
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


## Tests for irods commandds
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
    result = runner.invoke(cli, ["irods", "iget-fastqs", "--help"])
    assert result.exit_code == 0
    assert "Show this message and exit" in result.output


## Tests for scrna commands
def test_cellbender():
    runner = CliRunner()
    result = runner.invoke(cli, ["scrna", "cellbender", "--help"])
    assert result.exit_code == 0
    assert "Show this message and exit" in result.output


def test_merge_h5ad():
    runner = CliRunner()
    result = runner.invoke(cli, ["scrna", "merge-h5ad", "--help"])
    assert result.exit_code == 0
    assert "Show this message and exit" in result.output


def test_scanpy():
    runner = CliRunner()
    result = runner.invoke(cli, ["scrna", "scanpy", "--help"])
    assert result.exit_code == 0
    assert "Show this message and exit" in result.output


## Tests for history commands
def test_history_clear():
    runner = CliRunner()
    result = runner.invoke(cli, ["history", "clear", "--help"])
    assert result.exit_code == 0
    assert "Show this message and exit" in result.output


def test_history_uid():
    runner = CliRunner()
    result = runner.invoke(cli, ["history", "uid", "--help"])
    assert result.exit_code == 0
    assert "Show this message and exit" in result.output


def test_history_view():
    runner = CliRunner()
    result = runner.invoke(cli, ["history", "view", "--help"])
    assert result.exit_code == 0
    assert "Show this message and exit" in result.output


## Tests for jobrunner commands
def test_run_notebook():
    runner = CliRunner()
    result = runner.invoke(cli, ["jobrunner", "run_notebook", "--help"])
    assert result.exit_code == 0
    assert "Show this message and exit" in result.output


def test_submit_job():
    runner = CliRunner()
    result = runner.invoke(cli, ["jobrunner", "submit_job", "--help"])
    assert result.exit_code == 0
    assert "Show this message and exit" in result.output
