import subprocess

import click
import pandas as pd
from tabulate import tabulate

from solosis.utils.state import logger


def collect_samples(sample, samplefile):
    """Collects sample IDs from command-line input or a file."""
    samples = []

    if sample:
        samples.append(sample)

    if samplefile:
        try:
            sep = (
                ","
                if samplefile.endswith(".csv")
                else "\t" if samplefile.endswith(".tsv") else None
            )
            if sep is None:
                logger.error(
                    "Unsupported file format. Please provide a .csv or .tsv file"
                )
                return []

            df = pd.read_csv(samplefile, sep=sep)
            if "sample_id" in df.columns:
                samples.extend(df["sample_id"].dropna().astype(str).tolist())
            else:
                logger.error("File must contain a 'sample_id' column")
                return []
        except Exception as e:
            logger.error(f"Error reading sample file: {e}")
            return []

    if not samples:
        logger.error("No samples provided. Use --sample or --samplefile")
        raise click.Abort()

    return samples


def process_metadata_file(metadata, required_columns=None):
    """
    Collects samples from metadata file, ensuring required columns are included.

    Args:
        metadata (str): Path to metadata CSV/TSV file.
        required_columns (set or list, optional): Columns that must be present
            in the metadata file and included in the return object.
            Defaults to {"sample_id", "cellranger_dir"}.
    """
    if required_columns is None:
        required_columns = {"sample_id", "cellranger_dir"}
    else:
        required_columns = set(required_columns)

    samples = []

    if metadata:
        try:
            sep = (
                ","
                if metadata.endswith(".csv")
                else "\t" if metadata.endswith(".tsv") else None
            )
            if sep is None:
                logger.error(
                    "Unsupported file format. Please provide a .csv or .tsv file"
                )
                return []

            df = pd.read_csv(metadata, sep=sep)

            # Check for missing required columns
            missing = required_columns - set(df.columns)
            if missing:
                logger.warning(
                    f"Metadata file {metadata} is missing required columns: {', '.join(missing)}"
                )
            else:
                # Iterate rows, build dict with only required columns
                for _, row in df.iterrows():
                    if all(row.get(col) for col in required_columns):
                        sample = {col: row[col] for col in required_columns}
                        samples.append(sample)
                    else:
                        logger.warning(
                            f"Invalid entry (missing required values): {row}"
                        )
        except Exception as e:
            logger.error(f"Error reading metadata file {metadata}: {e}")

    if not samples:
        logger.error("No valid samples provided. Use --metadata")
        raise click.Abort()

    return samples


def process_h5_file(metadata, required_columns=None):
    """
    Collects samples from metadata file, ensuring required columns are included.

    Args:
        metadata (str): Path to metadata CSV/TSV file.
        required_columns (set or list, optional): Columns that must be present
            in the metadata file and included in the return object.
            Defaults to {"sample_id", "h5_path"}.
    """
    if required_columns is None:
        required_columns = {"sample_id", "h5_path"}
    else:
        required_columns = set(required_columns)

    samples = []

    if metadata:
        try:
            sep = (
                ","
                if metadata.endswith(".csv")
                else "\t" if metadata.endswith(".tsv") else None
            )
            if sep is None:
                logger.error(
                    "Unsupported file format. Please provide a .csv or .tsv file"
                )
                return []

            df = pd.read_csv(metadata, sep=sep)

            # Check for missing required columns
            missing = required_columns - set(df.columns)
            if missing:
                logger.warning(
                    f"Metadata file {metadata} is missing required columns: {', '.join(missing)}"
                )
            else:
                # Iterate rows, build dict with only required columns
                for _, row in df.iterrows():
                    if all(row.get(col) for col in required_columns):
                        sample = {col: row[col] for col in required_columns}
                        h5_path = str(sample.get("h5_path", "")).strip()
                        if not h5_path.endswith(".h5"):
                            logger.warning(
                                f"Invalid h5_path (must end with .h5): {h5_path}"
                            )
                            continue  # skip this entry

                        samples.append(sample)
                    else:
                        logger.warning(
                            f"Invalid entry (missing required values): {row}"
                        )
        except Exception as e:
            logger.error(f"Error reading metadata file {metadata}: {e}")

    if not samples:
        logger.error("No valid samples provided. Use --metadata")
        raise click.Abort()

    return samples


def validate_irods_path(sample_id, irods_path):
    """Validate that irods_path exists in imeta query results for sample_id."""
    try:
        cmd = ["imeta", "qu", "-C", "-z", "/seq/illumina", "sample", "=", sample_id]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)

        matches = [
            line.replace("collection: ", "").strip()
            for line in result.stdout.splitlines()
            if line.startswith("collection: ")
        ]

        if irods_path not in matches:
            logger.error(
                f"Provided iRODS path '{irods_path}' does not match any known collections for sample_id '{sample_id}'."
            )
            raise click.Abort()

        logger.debug(f"Validated iRODS path '{irods_path}' for sample_id '{sample_id}'")
        return True

    except subprocess.CalledProcessError as e:
        logger.error(f"Error running imeta command: {e.stderr.strip()}")
        raise click.Abort()


def validate_library_type(tsv_file):
    """
    Validates that each sample ID in the TSV file has only one unique library_type.
    If multiple library_type values are found for a sample ID, the process is aborted.

    :param tsv_file: Path to the TSV file
    """
    df = pd.read_csv(tsv_file, sep="\t", dtype=str)

    # Count unique library_type values for each sample
    invalid_samples = df.groupby("sample")["library_type"].nunique()
    invalid_samples = invalid_samples[invalid_samples > 1]

    if not invalid_samples.empty:
        invalid_samples_df = invalid_samples.reset_index()
        invalid_samples_df.columns = ["Sample ID", "Library Type Count"]
        logger.error(
            "The following sample IDs have multiple library types, and will now terminate:"
        )
        table = tabulate(
            invalid_samples_df,
            headers="keys",
            tablefmt="pretty",
            numalign="left",
            stralign="left",
            showindex=False,
        )
        logger.error(f"Problematic samples... \n{table}")
        raise click.Abort()
