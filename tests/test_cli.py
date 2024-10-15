import click
from click.testing import CliRunner

from solosis.cli import cli


def test_version():
    runner = CliRunner()
    result = runner.invoke(cli, ["--version"])
    assert result.exit_code == 0
    assert "version 0.1.0" in result.output


def test_help():
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "Show this message and exit" in result.output


def test_greet():
    runner = CliRunner()
    result = runner.invoke(cli, ["command-one", "--name", "Alice"])
    assert result.exit_code == 0
    assert "Hello, Alice!" in result.output


def test_read_file(tmp_path):
    # Create a temporary file
    test_file = tmp_path / "test.txt"
    test_file.write_text("Sample content")

    runner = CliRunner()
    result = runner.invoke(cli, ["command-two", str(test_file)])
    assert result.exit_code == 0
    assert "Sample content" in result.output
