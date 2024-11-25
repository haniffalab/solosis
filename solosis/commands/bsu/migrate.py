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
    "BSU Audit - Sequencing Runs!A2:Z20"  # Adjust range based on your sheet's data
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
        logger.error(f"Error listing files in SFTP path {path}: {e}")
        return [], 0


def list_irods_files(path):
    """List files in an iRODS directory using the 'ils' command."""
    logger.debug(f"Running 'ils' on path: {path}")
    try:
        result = subprocess.run(
            ["ils", path], capture_output=True, text=True, check=True
        )
        lines = result.stdout.strip().split("\n")
        files = [line.strip() for line in lines]
        logger.debug(f"Files from iRODS: {files}")
        return files
    except subprocess.CalledProcessError as e:
        logger.error(f"Error running ils: {e}")
        return []


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

    # Fetch headers to find the relevant column indices
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

    # Find column indices
    try:
        migrator_last_run_index = headers.index("Migrator Last Run")
        migrator_ftp_size_index = headers.index("Migrator FTP Size")
        migrator_fastqs_map_index = headers.index("Migrator FASTQs Map")

        migrator_cr_ftp_size_index = headers.index("CellRanger FTP Size")
        migrator_cr_files_map_index = headers.index("CellRanger Files Map")
    except ValueError as e:
        logger.error(
            '"Migrator" or "CellRanger" columns not found. Check the sheet headers.'
        )
        return

    # Fetch rows to process
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

    updated_values = []
    for row in rows:
        if len(row) < len(headers):
            row.extend([""] * (len(headers) - len(row)))  # Pad the row

        logger.info(f"Row Data: {row}")

        # FASTQ Paths
        sftp_path_fastq = row[headers.index("FTP Path FASTQs")].strip()
        irods_path_fastq = row[headers.index("iRods Path (FASTQs)")].strip()

        # CellRanger Paths
        sftp_path_cr = row[headers.index("FTP Path CellRanger")].strip()
        irods_path_cr = row[headers.index("iRods Path (CellRanger)")].strip()

        if not sftp_path_fastq or not irods_path_fastq:
            logger.warning(f"Skipping row with missing FASTQ paths.")
            continue

        # Handle FASTQ Comparison
        ftp_fastq_files, ftp_fastq_size = [], 0
        try:
            transport = paramiko.Transport((SFTP_HOST, SFTP_PORT))
            transport.connect(username=SFTP_USER, password=SFTP_PASS)
            sftp = paramiko.SFTPClient.from_transport(transport)

            ftp_fastq_files, ftp_fastq_size = list_sftp_files_and_size(
                sftp, sftp_path_fastq
            )
            logger.debug(f"ftp_fastq_files: {ftp_fastq_files}")
            sftp.close()
            transport.close()
        except Exception as e:
            logger.error(f"Failed to connect to SFTP server for FASTQs: {e}")

        irods_fastq_files = list_irods_files(irods_path_fastq)
        only_in_ftp_fastq, only_in_irods_fastq, common_fastq_files = compare_files(
            ftp_fastq_files, irods_fastq_files
        )

        logger.info("Files on FTP:")
        for file in sorted(ftp_fastq_files):
            logger.info(f"  - {file}")

        logger.info("Files on iRODS:")
        for file in sorted(irods_fastq_files):
            logger.info(f"  - {file}")

        row[migrator_fastqs_map_index] = (
            "No" if only_in_ftp_fastq or only_in_irods_fastq else "Yes"
        )
        row[migrator_last_run_index] = timestamp
        row[migrator_ftp_size_index] = human_readable_size(ftp_fastq_size)

        # Handle CellRanger Comparison (if paths exist)
        if sftp_path_cr and irods_path_cr:
            ftp_cr_files, ftp_cr_size = [], 0
            try:
                transport = paramiko.Transport((SFTP_HOST, SFTP_PORT))
                transport.connect(username=SFTP_USER, password=SFTP_PASS)
                sftp = paramiko.SFTPClient.from_transport(transport)

                ftp_cr_files, ftp_cr_size = list_sftp_files_and_size(sftp, sftp_path_cr)
                sftp.close()
                transport.close()
            except Exception as e:
                logger.error(f"Failed to connect to SFTP server for CellRanger: {e}")

            irods_cr_files = list_irods_files(irods_path_cr)
            only_in_ftp_cr, only_in_irods_cr, common_cr_files = compare_files(
                ftp_cr_files, irods_cr_files
            )

            logger.info("CellRanger on FTP:")
            for file in sorted(ftp_cr_files):
                logger.info(f"  - {file}")

            logger.info("CellRanger on iRODS:")
            for file in sorted(irods_cr_files):
                logger.info(f"  - {file}")

            row[migrator_cr_files_map_index] = (
                "No" if only_in_ftp_cr or only_in_irods_cr else "Yes"
            )
            row[migrator_cr_ftp_size_index] = human_readable_size(ftp_cr_size)

        updated_values.append(row)

    # Update Google Sheet
    update_google_sheet(service, SPREADSHEET_ID, RANGE_NAME, updated_values)


if __name__ == "__main__":
    main()
