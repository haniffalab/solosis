import os
import subprocess

import click
import pandas as pd

from solosis.utils.logging_utils import secho


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
                secho(
                    "Unsupported file format. Please provide a .csv or .tsv file",
                    "error",
                )
                return []

            df = pd.read_csv(samplefile, sep=sep)
            if "sample_id" in df.columns:
                samples.extend(df["sample_id"].dropna().astype(str).tolist())
            else:
                secho("File must contain a 'sample_id' column", "error")
                return []
        except Exception as e:
            secho(f"Error reading sample file: {e}", "error")
            return []

    if not samples:
        secho("No samples provided. Use --sample or --samplefile", "error")
        click.Abort()

    return samples
