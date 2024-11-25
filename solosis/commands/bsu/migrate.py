import datetime
import logging
import math
import os
import subprocess

import pandas as pd
import paramiko
from google.auth.transport import requests
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

# Google Sheets API details
CREDENTIALS_PATH = (
    "sanger-development-1004c2b78a53.json"  # Path to your service account credentials
)
SPREADSHEET_ID = (
    "1UAaedFI3aE_M1iDMar6gCrzAHB_ZUoJcsB3Z15p45gc"  # Replace with your Google Sheet ID
)
RANGE_NAME = (
    "BSU Audit - Sequencing Runs!A2:Z3"  # Adjust range based on your sheet's data
)

# SFTP server details
SFTP_HOST = "bsu.ncl.ac.uk"
SFTP_PORT = 22
SFTP_USER = os.getenv("FTP_USER")  # Fetch SFTP username from environment variable
SFTP_PASS = os.getenv("FTP_PASS")  # Fetch SFTP password from environment variable


def human_readable_size(size_bytes):
    """Convert bytes to a human-readable format."""
    if size_bytes == 0:
        return "0.00 B"
    size_units = ["B", "KB", "MB", "GB", "TB"]
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_units[i]}"


def list_sftp_files_and_size(sftp, path):
    """List files in an SFTP directory and calculate total size."""
    total_size = 0
    file_list = []
    try:
        for entry in sftp.listdir_attr(path):
            file_name = entry.filename
            file_size = entry.st_size
            total_size += file_size
            file_list.append((file_name, file_size))
        return file_list, total_size
    except Exception as e:
        logger.error(f"Error listing files in FTP path {path}: {e}")
        return [], 0


def list_irods_files(path):
    """List files in an iRODS directory using the 'ils' command."""
    logger.debug(f"Running 'ils' on path: {path}")
    try:
        result = subprocess.run(
            ["ils", path], capture_output=True, text=True, check=True
        )
        lines = result.stdout.strip().split("\n")
        files = [line.strip() for line in lines if not line.strip().endswith(":")]
        logger.debug(f"Files from iRODS: {files}")
        return files
    except subprocess.CalledProcessError as e:
        logger.error(f"Error running ils: {e}")
        return []


def get_irods_metadata(file_path, irods_base_path):
    """Retrieve and return metadata for a file in iRODS."""
    # Strip spaces and remove multiple spaces within the path
    full_path = os.path.join(irods_base_path, file_path).strip()
    try:
        result = subprocess.run(
            ["imeta", "ls", "-d", full_path], capture_output=True, text=True, check=True
        )
        metadata = result.stdout.strip()
        if metadata:
            logger.debug(f"Metadata for {full_path}: {metadata}")
        else:
            logger.debug(f"No metadata found for {full_path}")
        return metadata
    except subprocess.CalledProcessError as e:
        logger.error(f"Error retrieving metadata for {full_path}: {e}")
        return None


def compare_files(ftp_files, irods_files):
    """Compare files between FTP and iRODS."""
    ftp_file_names = {f[0] for f in ftp_files}
    irods_file_names = {os.path.basename(f) for f in irods_files}

    only_in_ftp = ftp_file_names - irods_file_names
    only_in_irods = irods_file_names - ftp_file_names
    common_files = ftp_file_names & irods_file_names

    return only_in_ftp, only_in_irods, common_files


def authenticate_google_sheets():
    """Authenticate using a service account and return the Google Sheets service."""
    creds = Credentials.from_service_account_file(
        CREDENTIALS_PATH,
        scopes=["https://www.googleapis.com/auth/spreadsheets"],
    )
    service = build("sheets", "v4", credentials=creds)
    return service


def update_google_sheet(service, sheet_id, range_name, values):
    """Update the Google Sheet with the new values (including timestamp)."""
    try:
        body = {"values": values}
        result = (
            service.spreadsheets()
            .values()
            .update(
                spreadsheetId=sheet_id,
                range=range_name,
                body=body,
                valueInputOption="RAW",
            )
            .execute()
        )
        logger.info(f"{result.get('updatedCells')} cells updated.")
    except HttpError as err:
        logger.error(f"Error updating sheet: {err}")


def main():
    # Authenticate with Google Sheets API
    service = authenticate_google_sheets()
    logger.info("Successfully authenticated with Google Sheets API.")

    # Fetch headers to find the "Migrator Last Run" column index
    try:
        sheet = (
            service.spreadsheets()
            .values()
            .get(
                spreadsheetId=SPREADSHEET_ID, range="BSU Audit - Sequencing Runs!A1:Z1"
            )
            .execute()
        )
        headers = sheet.get("values", [])[0]  # Get the first row as headers
    except HttpError as err:
        logger.error(f"Error fetching data from Google Sheets: {err}")
        return

    if not headers:
        logger.error("No headers found in the Google Sheets.")
        return

    # Find the index of the "Migrator Last Run" column
    try:
        migrator_last_run_index = headers.index("Migrator Last Run")
    except ValueError:
        logger.error('"Migrator Last Run" column not found.')
        return

    # Fetch the rows to process
    try:
        sheet = (
            service.spreadsheets()
            .values()
            .get(
                spreadsheetId=SPREADSHEET_ID, range="BSU Audit - Sequencing Runs!A2:Z3"
            )
            .execute()
        )
        rows = sheet.get("values", [])
    except HttpError as err:
        logger.error(f"Error fetching data from Google Sheets: {err}")
        return

    if not rows:
        logger.error("No data found in the Google Sheets.")
        return

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Process the rows
    updated_values = []
    for row in rows:
        # if len(row) < len(headers):
        #     logger.warning("Skipping row with insufficient data.")
        #     continue  # Skip rows with insufficient data

        # Get the SFTP and iRODS paths from the current row
        sftp_path = (
            row[headers.index("FTP Path FASTQs")].strip()
            if row[headers.index("FTP Path FASTQs")]
            else None
        )
        irods_path = (
            row[headers.index("iRods Path (FASTQs)")].strip()
            if row[headers.index("iRods Path (FASTQs)")]
            else None
        )

        if not sftp_path or not irods_path:
            logger.warning(f"Skipping row with missing paths.")
            continue

        logger.info(
            f"Processing row: SFTP Path - {sftp_path}, iRODS Path - {irods_path}"
        )

        # Set up SFTP connection
        try:
            logger.info(f"Connecting to SFTP server: {SFTP_HOST}")
            transport = paramiko.Transport((SFTP_HOST, SFTP_PORT))
            transport.connect(username=SFTP_USER, password=SFTP_PASS)
            sftp = paramiko.SFTPClient.from_transport(transport)
            logger.info("Connected to SFTP server successfully.")
        except Exception as e:
            logger.error(f"Failed to connect to SFTP server: {e}")
            continue  # Skip this row if connection fails

        # List files in the SFTP directory and calculate total size
        ftp_files, ftp_total_size = list_sftp_files_and_size(sftp, sftp_path)
        logger.info(f"Files in FTP path {sftp_path}:")
        for file_name, file_size in ftp_files:
            logger.info(f"- {file_name} ({human_readable_size(file_size)})")
        logger.info(
            f"Total size of FTP directory {sftp_path}: {human_readable_size(ftp_total_size)}"
        )

        # Close SFTP connection
        sftp.close()
        transport.close()

        # List files in the iRODS directory
        irods_files = list_irods_files(irods_path)
        logger.info(f"Files in iRODS path {irods_path}: {irods_files}")

        # Compare files
        only_in_ftp, only_in_irods, common_files = compare_files(ftp_files, irods_files)
        logger.info(f"Files only in FTP: {only_in_ftp}")
        logger.info(f"Files only in iRODS: {only_in_irods}")
        logger.info(f"Files in both FTP and iRODS: {common_files}")

        # Add the timestamp to the row's "Migrator Last Run" column
        row[migrator_last_run_index] = timestamp

        updated_values.append(row)

    # Update the Google Sheet with the new data
    update_google_sheet(service, SPREADSHEET_ID, RANGE_NAME, updated_values)


if __name__ == "__main__":
    main()
