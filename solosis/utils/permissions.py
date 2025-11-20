import getpass
import os
import subprocess

import click

from solosis.utils.state import logger


def set_team_data_acl(dir_path: str = None):
    """
    Apply ACLs to the TEAM_DATA_DIR.
    """
    if dir_path is None:
        dir_path = os.environ.get("TEAM_DATA_DIR")
        if not dir_path:
            raise ValueError("TEAM_DATA_DIR environment variable not set")

    try:
        subprocess.run(["setfacl", "-d", "-m", "g::rwX", dir_path], check=True)
        subprocess.run(["setfacl", "-d", "-m", "o::rX", dir_path], check=True)
        logger.info(f"ACLs applied recursively to TEAM_DATA_DIR: {dir_path}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to set ACLs on {dir_path}: {e}")
        raise
