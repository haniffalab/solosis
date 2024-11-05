#!/bin/bash
# submit.sh - Environment setup for pull-fastq processing using Nextflow

# Usage:
#   ./submit.sh <sample_ids>
#
# Parameters:
#   <sample_ids> - Comma-separated list of sample IDs to process.

# Exit immediately if a command exits with a non-zero status
set -e

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

# Load necessary modules
MODULES=("irods" "conda" "nextflow" "singularity")
for MODULE in "${MODULES[@]}"; do
  if ! module load cellgen/"$MODULE"; then
    echo "Error: Failed to load $MODULE module" >&2
    exit 1
  fi
done

# Configure paths and environment variables
export NXF_WORK="$HOME"
export LSB_DEFAULT_USERGROUP="team298"
export PATH="/software/singularity/v3.10.0/bin:$PATH"

TEAM_SAMPLE_DATA_DIR="/lustre/scratch126/cellgen/team298/data/samples"
TEAM_LOGS_DIR="$HOME/logs"

# Ensure logs directory exists
mkdir -p "$TEAM_LOGS_DIR"

# Define the output directory for Nextflow
OUTPUT_DIR="${TEAM_SAMPLE_DATA_DIR}/fastq"

# Create output directory if it does not exist
mkdir -p "$OUTPUT_DIR"

# Run pull-fastq Nextflow process with the sample list
echo "Running Nextflow process for samples: $SAMPLE_IDS"
nextflow run cellgeni/nf-irods-to-fastq -r main main.nf \
    --findmeta "$SAMPLE_IDS" \
    --cram2fastq \
    --publish_dir "$OUTPUT_DIR"

echo "All samples processed with Nextflow."