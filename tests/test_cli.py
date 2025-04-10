import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import click
from click.testing import CliRunner

from solosis.cli import cli

# responding to error message ("missing environmnet variables LSB_DEFAULT_USERGROUP and TEAM_DATA_DIR")
os.environ["LSB_DEFAULT_USERGROUP"] = "team298"
os.environ["TEAM_DATA_DIR"] = "/tmp/solosis"
# create /tmp/solosis
# Create directory structure
Path(os.environ["TEAM_DATA_DIR"]).mkdir(parents=True, exist_ok=True)
Path(f"{os.environ['TEAM_DATA_DIR']}/samples/sample_test/fastq").mkdir(
    parents=True, exist_ok=True
)
# Create empty file
file_path = Path(
    f"{os.environ['TEAM_DATA_DIR']}/samples/sample_test/fastq/sample_test.fastq.gz"
)
file_path.touch()
# create empty file /tmp/solosis/samples/sample_test/fastq/sample_test.fastq.gz sample that will pass
# sample that will fail "Sample_fail"
libraries_path = Path(f"{os.environ['TEAM_DATA_DIR']}/test_libraries.csv")
libraries_path.touch()


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


def test_cellranger_count_invalid_sample(caplog):
    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["alignment", "cellranger-count", "--sample", "fail-sample"],
        catch_exceptions=False,
    )  # Ensure exceptions are captured

    # Check if the process failed
    assert result.exit_code != 0  # Expected to fail

    # Capture the log output for the ERROR message
    with caplog.at_level("ERROR"):  # Capturing logs at ERROR level
        # Now the logs should contain the expected error message
        assert "No valid samples found. Exiting" in caplog.text


def test_cellranger_count_valid_sample(caplog):
    # make mock of subprocess.run to simulate a successful 'process'
    with patch("subprocess.run") as mock_run:
        # create a mock process object with stdout (was failing without)
        mock_process = MagicMock()
        mock_process.stdout = "Job submitted successfully"

        # Mock subprocess.run to return mock process (instead of executing the command)
        mock_run.return_value = mock_process

        runner = CliRunner()
        result = runner.invoke(
            cli,
            ["alignment", "cellranger-count", "--sample", "sample_test"],
            catch_exceptions=False,
        )  # Ensure exceptions are captured

        # Check if the process succeeded
        assert result.exit_code == 0
        # Capture the log output for the success message
        with caplog.at_level("INFO"):  # Capturing logs at INFO level
            assert "Job submitted successfully" in caplog.text


## Tests for alignment commands
# cellranger-arc-count
def test_cellranger_arc_count():
    runner = CliRunner()
    result = runner.invoke(cli, ["alignment", "cellranger-arc-count", "--help"])
    assert result.exit_code == 0
    assert "Show this message and exit" in result.output


def test_cellranger_arc_count_invalid_libraries(caplog):
    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["alignment", "cellranger-arc-count", "--libraries", "test.csv"],
        catch_exceptions=False,
    )  # Ensure exceptions are captured

    # Check if the process failed
    assert result.exit_code != 0  # Expected to fail

    # Capture the log output for the ERROR message
    with caplog.at_level("ERROR"):  # Capturing logs at ERROR level
        # Now the logs should contain the expected error message
        assert "Invalid value for '--libraries': Path" in result.output


def test_cellranger_arc_count_valid_sample(caplog):
    # make mock of subprocess.run to simulate a successful 'process'
    with patch("subprocess.run") as mock_run:
        # create a mock process object with stdout (was failing without)
        mock_process_arc = MagicMock()
        mock_process_arc.stdout = "Job submitted successfully"

        # Mock subprocess.run to return mock process (instead of executing the command)
        mock_run.return_value = mock_process_arc

        runner = CliRunner()
        result = runner.invoke(
            cli,
            ["alignment", "cellranger-arc-count", "--libraries", libraries_path],
            catch_exceptions=False,
        )  # Ensure exceptions are captured

        # Check if the process succeeded
        assert result.exit_code != 0
        # Capture the log output for the success message
        with caplog.at_level("ERROR"):  # Capturing logs at INFO level
            assert "No valid libraries files found. Exiting" in caplog.text


# cellranger-vdj
def test_cellranger_vdj():
    runner = CliRunner()
    result = runner.invoke(cli, ["alignment", "cellranger-vdj", "--help"])
    assert result.exit_code == 0
    assert "Show this message and exit" in result.output


def test_cellranger_vdj_invalid_sample(caplog):
    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["alignment", "cellranger-vdj", "--sample", "fail-sample"],
        catch_exceptions=False,
    )  # Ensure exceptions are captured

    # Check if the process failed
    assert result.exit_code != 0  # Expected to fail

    # Capture the log output for the ERROR message
    with caplog.at_level("ERROR"):  # Capturing logs at ERROR level
        # Now the logs should contain the expected error message
        assert "No valid samples found. Exiting" in caplog.text


def test_cellranger_vdj_valid_sample(caplog):
    # make mock of subprocess.run to simulate a successful 'process'
    with patch("subprocess.run") as mock_run:
        # create a mock process object with stdout (was failing without)
        mock_process = MagicMock()
        mock_process.stdout = "Job submitted successfully"

        # Mock subprocess.run to return mock process (instead of executing the command)
        mock_run.return_value = mock_process

        runner = CliRunner()
        result = runner.invoke(
            cli,
            ["alignment", "cellranger-vdj", "--sample", "sample_test"],
            catch_exceptions=False,
        )  # Ensure exceptions are captured

        # Check if the process succeeded
        assert result.exit_code == 0
        # Capture the log output for the success message
        with caplog.at_level("INFO"):  # Capturing logs at INFO level
            assert "Job submitted successfully" in caplog.text


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
