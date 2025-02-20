import tomllib

from solosis.utils.logging_utils import setup_logging

logger, execution_uid = setup_logging()


def get_version():
    try:
        with open("pyproject.toml", "rb") as f:
            data = tomllib.load(f)
        return data.get("project", {}).get("version", "unknown")
    except Exception as e:
        logger.error(f"Error reading version from pyproject.toml: {e}")
        return "unknown"


version = get_version()
