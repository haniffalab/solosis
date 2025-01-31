#!/bin/bash
# submit.sh - Environment setup for imeta-report command

# Usage:
#   ./submit.sh <sample_ids>
#
# Parameters:
#   <sample_ids> - Comma-separated list of sample IDs to process.

set -e  # Exit on error

# Ensure at least one argument is provided
if [ "$#" -lt 1 ]; then
  echo "Usage: $0 <sample_ids>" >&2
  exit 1
fi

# Assign command-line argument to variable
SAMPLE_IDS="$1"

# Verify that the sample list is not empty
if [ -z "$SAMPLE_IDS" ]; then
  echo "Error: No samples provided." >&2
  exit 1
fi

# Load irods module
if ! module load cellgen/irods; then
  echo "Error: Failed to load irods module" >&2
  exit 1
fi

# Define directories
TEAM_SAMPLE_DATA_DIR="/lustre/scratch126/cellgen/team298/data/samples"
TEAM_LOGS_DIR="/lustre/scratch126/cellgen/team298/logs"

# Ensure logs directory exists
mkdir -p "$TEAM_LOGS_DIR"

# Convert comma-separated sample IDs into an array
IFS=',' read -r -a SAMPLES <<< "$SAMPLE_IDS"

# Process each sample individually
for SAMPLE in "${SAMPLES[@]}"; do
    echo "Processing sample: $SAMPLE"

    # Define sample-specific output directory
    OUTPUT_DIR="${TEAM_SAMPLE_DATA_DIR}/${SAMPLE}/cellranger"
    mkdir -p "$OUTPUT_DIR"
    cd "$OUTPUT_DIR"

    # Find Cell Ranger outputs
    imeta qu -C -z /seq/illumina sample = "$SAMPLE" | \
    grep "^collection: " | sed 's/^collection: //' > "cellranger_path.csv"

    # Check if cellranger_path.csv is empty
    if [ -s "cellranger_path.csv" ]; then
      cellranger_avail="yes"
    else
      cellranger_avail="no"
    fi

    # Find FASTQ/CRAM files
    imeta qu -d -z /seq sample = "$SAMPLE" | \
    grep "^collection: " | sed 's/^collection: //' > "cram_path.csv"

    # Check if cram_path.csv is empty
    if [ -s "cram_path.csv" ]; then
      cram_avail="yes"
    else
      cram_avail="no"
    fi

    # Determine iRODS availability
    if [ "$cellranger_avail" = "yes" ] || [ "$cram_avail" = "yes" ]; then
      irods_avail="yes"
    else
      irods_avail="no"
    fi

    # Confirm saved outputs
    num_cellranger_paths=$(wc -l < cellranger_path.csv)
    num_cram_paths=$(wc -l < cram_path.csv)

    echo "Saved $num_cellranger_paths matching path(s) to $OUTPUT_DIR/cellranger_path.csv."
    echo "Saved $num_cram_paths matching path(s) to $OUTPUT_DIR/cram_path.csv."

    # Write to report
    if [ ! -f "irods_report.txt" ]; then
        printf "%-15s %-10s %-10s %-10s\n" "Samples" "iRODS" "CRAM" "CellRanger" > irods_report.txt
        printf "%-15s %-10s %-10s %-10s\n" "---------" "-------" "-------" "---------" >> irods_report.txt
    fi
    printf "%-15s %-10s %-10s %-10s\n" "$SAMPLE" "$irods_avail" "$cram_avail" "$cellranger_avail" >> irods_report.txt

done  # End sample loop

echo "Processing completed. Report saved in irods_report.txt"
