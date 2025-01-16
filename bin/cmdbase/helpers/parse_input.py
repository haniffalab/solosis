#!/usr/bin/env python3

import csv
import logging
import os

SAMPLE_HEADERS = [  # Lowercase and in expected order if input has no header
    "sample_id",
    "sample_name",
    "cellranger_path",
]
DELIMITER = ","


def clean_reader(reader: csv.reader) -> csv.reader:
    """
    Strips leading and trailing spaces from all values in a csv.reader object.
    Lowercases headers if the reader is a csv.DictReader object.

    Args:
        reader (csv.reader or csv.DictReader): The CSV reader object.

    Yields:
        dict or list: The row with stripped spaces.
    """
    for row in reader:
        if isinstance(row, dict):
            yield {k.strip().lower(): v.strip() for k, v in row.items()}
        else:
            yield [v.strip() for v in row]


def parse_input(
    path: str,
    output_dir: str,
    output_filename: str,  # @TODO: set default
    delimiter: str = ",",
    has_header: bool = True,
    clean_values: bool = True,
) -> str:
    """
    Loads a tsv/csv file and generates a standard csv file with headers:
    `sample_id`, `sample_name`, `cellranger_path`.

    Args:
        path (str): The path to the input CSV file.
        output_dir (str): The directory where the output CSV file will be saved.
        output_filename (str): The name of the output CSV file.
        delimiter (str, optional): The delimiter used in the CSV file.
            Defaults to ",".
        has_header (bool, optional): Whether the CSV file has a header row.
            Defaults to True.
        clean_values (bool, optional): Whether to strip leading and trailing spaces
            from each field and lowercase headers (if present). Defaults to True.

    Returns:
        str: The path to the generated CSV file.
    """
    with open(path, "r") as f:
        if has_header:
            logging.info(f"Reading file with header and delimiter {delimiter}")
            reader = csv.DictReader(f, delimiter=delimiter)
        else:
            logging.info(f"Reading file without header and delimiter {delimiter}")
            reader = csv.reader(f, delimiter=delimiter)
        reader = clean_reader(reader) if clean_values else reader

        output_filename = (
            output_filename
            if output_filename.endswith(".csv")
            else f"{output_filename}.csv"
        )

        # @TODO: determine required values -> throw error if not found
        # @TODO: use sample_id as sample_name if not present
        logging.info(f"Writing to file {os.path.join(output_dir,output_filename)}")
        logging.info(f"Writing headers: {SAMPLE_HEADERS}")
        with open(os.path.join(output_dir, output_filename), "w") as out_csv:
            writer = csv.writer(out_csv, delimiter=DELIMITER)
            writer.writerow(SAMPLE_HEADERS)
            for row in reader:
                parsed_row = []
                for i, header in enumerate(SAMPLE_HEADERS):
                    if has_header:
                        parsed_row.append(row.get(header, None))
                    else:
                        parsed_row.append(row[i] if i < len(row) else None)
                writer.writerow(parsed_row)
