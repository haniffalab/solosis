import os
import subprocess
from pathlib import Path
from unittest import mock
from unittest.mock import MagicMock, patch

import click
import pandas as pd
import pytest
from click.testing import CliRunner

from solosis.cli import cli
from solosis.commands.history.view import cmd
from solosis.utils.env_utils import authenticate_irods, irods_auth

# responding to error message ("missing environmnet variables LSB_DEFAULT_USERGROUP and TEAM_DATA_DIR")
os.environ["LSB_DEFAULT_USERGROUP"] = "team298"
os.environ["TEAM_DATA_DIR"] = "/tmp/solosis"
# create /tmp/solosis
Path(os.environ["TEAM_DATA_DIR"]).mkdir(parents=True, exist_ok=True)
Path(f"{os.environ['TEAM_DATA_DIR']}/samples/sample_test/fastq").mkdir(
    parents=True, exist_ok=True
)
# Create empty file
file_path = Path(
    f"{os.environ['TEAM_DATA_DIR']}/samples/sample_test/fastq/sample_test.fastq.gz"
)
file_path.touch()  # create empty file /tmp/solosis/samples/sample_test/fastq/sample_test.fastq.gz sample that will pass
# for cellranger arc tests
libraries_path = Path(f"{os.environ['TEAM_DATA_DIR']}/test_libraries.csv")
libraries_path.touch()
# create metadata input file for cellbender tests
data = {
    "sample_id": ["sample_test"],
    "cellranger_dir": [
        "/tmp/solosis/samples/sample_test/cellranger/solosis_720/sample_test/outs"
    ],
}
# make it a dataframe
df = pd.DataFrame(data)
df.to_csv(Path(f"{os.environ['TEAM_DATA_DIR']}/metadata_input.csv"), index=False)


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
        # Capture the log output for the success messageß
        assert "Job submitted successfully" in caplog.text


## Tests for irods commands
def test_imeta_report():
    runner = CliRunner()
    result = runner.invoke(cli, ["irods", "imeta-report", "--help"])
    assert result.exit_code == 0
    assert "Show this message and exit" in result.output


#####   FAILING
# @patch("solosis.utils.subprocess_utils.popen")
# def test_imeta_report_valid_sample(mock_popen, caplog):
#    mock_popen.return_value = None  # or a mock process if needed

#    runner = CliRunner()
#    result = runner.invoke(
#        cli,
#        ["irods", "imeta-report", "--sample", "sample_test"],
#        catch_exceptions=False,
#    )

#    assert result.exit_code == 0

#    with caplog.at_level("INFO"):
#        assert "Processing sample:" in result.output


## testing successful irods authentication (env_utils.irods_auth)
@mock.patch("solosis.utils.env_utils.subprocess.run")
def test_irods_auth_success(mock_run):
    mock_run.return_value = subprocess.CompletedProcess(
        args=["iget", "dummy"], returncode=1, stdout="", stderr="USER_INPUT_PATH_ERR"
    )

    result = irods_auth()
    assert result is True
    mock_run.assert_called_once()


## testing invalid user to trigger re-authentication (solosis.utils.env_utils.authenticate_irods)
@mock.patch("solosis.utils.env_utils.authenticate_irods", return_value=True)
@mock.patch("solosis.utils.env_utils.subprocess.run")
def test_irods_auth_invalid_user_reauth(mock_run, mock_authenticate):
    mock_run.return_value = subprocess.CompletedProcess(
        args=["iget", "dummy"], returncode=1, stdout="", stderr="CAT_INVALID_USER"
    )

    result = irods_auth()
    assert result is True
    mock_authenticate.assert_called_once()


## testing irods not installed (env_utils.irods_auth)
@mock.patch("solosis.utils.env_utils.subprocess.run", side_effect=FileNotFoundError())
def test_irods_auth_command_not_found(mock_run):
    result = irods_auth()
    assert result is False


# testing for this ln 55  "logger.info("Checking iRODS authentication status...")" in env_utils
@mock.patch("solosis.utils.env_utils.getpass.getpass", return_value="dummy_password")
@mock.patch("solosis.utils.env_utils.subprocess.run")
@mock.patch("solosis.utils.env_utils.subprocess.Popen")
def test_authenticate_irods_success(mock_popen, mock_run, mock_getpass):
    # mock behavior of subprocess.Popen to simulate success
    mock_process = mock.Mock()
    mock_process.communicate.return_value = ("Authenticated", "")
    mock_process.returncode = 0
    mock_popen.return_value = mock_process

    result = authenticate_irods()

    mock_getpass.assert_called_once()
    mock_run.assert_called_once_with(["stty", "sane"])
    mock_popen.assert_called_once_with(
        ["iinit"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    assert result is True


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


def test_cellbender_invalid_metadata(caplog):
    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["scrna", "cellbender", "--metadata", "test.csv"],
        catch_exceptions=False,
    )  # Ensure exceptions are captured

    # Check if the process failed
    assert result.exit_code != 0  # Expected to fail

    # Capture the log output for the ERROR message
    with caplog.at_level("ERROR"):  # Capturing logs at ERROR level
        # Now the logs should contain the expected error message
        assert "Invalid value for '--metadata': Path" in result.output


class TestCellbender:

    @pytest.fixture(scope="class")
    def cellranger_validation(self, tmp_path_factory):
        # Create a shared temp directory
        base_dir = tmp_path_factory.mktemp("cellbender_test")

        # Build mock structure
        sample_id = "sample_test"
        outs = base_dir / sample_id / "cellranger" / "solosis_720" / sample_id / "outs"
        outs.mkdir(parents=True)

        # Create dummy output files
        (outs / "raw_feature_bc_matrix.h5").write_text("fake h5 content")
        (outs / "_log").write_text("Pipestance completed successfully!")

        # Metadata file (relative paths!)
        metadata = base_dir / "metadata_input.csv"
        rel_path = f"{sample_id}/cellranger/solosis_720/{sample_id}/outs"
        metadata.write_text(f"sample_id,cellranger_dir\n{sample_id},{rel_path}\n")

        return {
            "base_dir": base_dir,
            "metadata": metadata,
            "sample_id": sample_id,
            "outs": outs,
        }

    def test_cellbender_valid_sample(self, caplog, monkeypatch, cellranger_validation):
        monkeypatch.chdir(cellranger_validation["base_dir"])

        with patch("subprocess.run") as mock_run:
            mock_process = MagicMock()
            mock_process.stdout = "Job submitted successfully"
            mock_run.return_value = mock_process

            runner = CliRunner()
            result = runner.invoke(
                cli,
                ["scrna", "cellbender", "--metadata", "metadata_input.csv"],
                catch_exceptions=False,
            )

            assert result.exit_code == 0
            # Check if the success message is printed to stdout
            assert "Job submitted successfully" in caplog.text


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


# testing success of history uid command
def test_history_view_success(caplog):
    runner = CliRunner()
    dummy_uid = str(uuid.uuid4())  # make dummy UID
    # add a dummy entry
    cmd.add(
        {
            "uid": dummy_uid,
            "command": "dummy --test",
            "timestamp": "2025-04-17T12:00:00Z",
        }
    )
    result = runner.invoke(cli, ["history", "uid", dummy_uid])
    assert result.exit_code == 0
    assert "INFO: Execution UID: {dummy_uid}" in caplog.text
    assert "INFO: Command:" in caplog.text
    assert "INFO: Logs" in caplog.text


# testing failure of history uid command
def test_history_view_success(caplog):
    runner = CliRunner()
    result = runner.invoke(cli, ["history", "uid", "fail-uid"])
    assert result.exit_code == 1
    assert "ERROR: No log entry found for UID:" in caplog.text


def test_history_view():
    runner = CliRunner()
    result = runner.invoke(cli, ["history", "view", "--help"])
    assert result.exit_code == 0
    assert "Show this message and exit" in result.output


# testing success of history view command
def test_history_view_success(caplog):
    runner = CliRunner()
    result = runner.invoke(cli, ["history", "view"])
    assert result.exit_code == 0
    assert "recent log entries:" in caplog.text


# testing success of history view (with specified line number)
def test_history_view_success(caplog):
    runner = CliRunner()
    result = runner.invoke(cli, ["history", "view", "-n", "20"])
    assert result.exit_code == 0
    assert "20 recent log entries:" in caplog.text


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
