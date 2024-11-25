import logging
import math
import os
import subprocess

import pandas as pd
import paramiko

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

# CSV file path
csv_path = "audit.csv"

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


def main():
    # Load the CSV file
    df = pd.read_csv(csv_path)

    # Process the first two rows
    for index, row in df.head(2).iterrows():  # This will loop over the first two rows
        # Get the SFTP and iRODS paths from the current row
        sftp_path = row["FTP Path FASTQs"].strip()
        irods_path = row["iRods Path (FASTQs)"].strip()

        logger.info(
            f"Processing row {index+1}: SFTP Path - {sftp_path}, iRODS Path - {irods_path}"
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
        logger.info(f"Files in iRODS path {irods_path}:")
        for file_name in irods_files:
            logger.info(f"- {file_name}")

            # Retrieve metadata for each iRODS file
            metadata = get_irods_metadata(file_name, irods_path)
            logger.info(f"Metadata for {file_name}: {metadata}")

        # Compare files between FTP and iRODS
        only_in_ftp, only_in_irods, common_files = compare_files(ftp_files, irods_files)

        if only_in_ftp:
            logger.warning("Files found in FTP but not in iRODS:")
            for file in only_in_ftp:
                logger.warning(f"FTP only: {file}")
        if only_in_irods:
            logger.warning("Files found in iRODS but not in FTP:")
            for file in only_in_irods:
                logger.warning(f"iRODS only: {file}")
        if common_files:
            logger.info("Common files between FTP and iRODS:")
            for file in common_files:
                logger.info(f"Common: {file}")
        else:
            logger.warning("No common files found between FTP and iRODS.")


if __name__ == "__main__":
    main()
