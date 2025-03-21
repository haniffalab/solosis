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


def process_metadata_file(metadata):
    """Collects samples from metadata file."""
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
            required_columns = {"sample_id", "cellranger_dir"}
            if not required_columns.issubset(df.columns):
                logger.warning(
                    f"Metadata file {metadata} is missing required columns: {', '.join(required_columns - set(df.columns))}"
                )
            else:
                # Loop through each row and validate the presence of 'sample_id' and 'cellranger_dir'
                for _, row in df.iterrows():
                    sample_id = row.get("sample_id")
                    cellranger_dir = row.get("cellranger_dir")

                    # Check if both values are present and non-empty
                    if sample_id and cellranger_dir:
                        samples.append(
                            {
                                "sample_id": sample_id,
                                "cellranger_dir": cellranger_dir,
                            }
                        )
                    else:
                        logger.warning(
                            f"Invalid entry (missing sample_id or cellranger_dir): {row}"
                        )
        except Exception as e:
            logger.error(f"Error reading metadata file {samples}: {e}")

    if not samples:
        logger.error("No samples provided. Use --metadata")
        raise click.Abort()

    return samples


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
        logger.info(f"Problematic samples... \n{table}")
        raise click.Abort()
