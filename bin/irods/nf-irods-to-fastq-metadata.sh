#!/bin/bash
# submit.sh - Environment setup for pull-fastq processing using Nextflow

# Usage:
#   ./submit.sh <sample_file> <random_id>
#
# Parameters:
#   <sample_file> - Path to a file containing sample IDs, one per line.
#   <random_id> - A unique 8-character identifier for this run.

# Exit immediately if a command exits with a non-zero status
set -e

# Ensure exactly two arguments are provided
if [ "$#" -ne 2 ]; then
  echo "Usage: $0 <sample_file> <random_id>" >&2
  exit 1
fi

# Assign command-line arguments to variables
SAMPLE_FILE="$1"
RANDOM_ID="$2"

# Verify that the sample file exists and is not empty
if [ ! -f "$SAMPLE_FILE" ] || [ ! -s "$SAMPLE_FILE" ]; then
  echo "Error: Sample file '$SAMPLE_FILE' does not exist or is empty." >&2
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

# Setup Nextflow work directory
mkdir -p "$TEAM_TMP_DIR/nxf"
chmod -R g+w "$TEAM_TMP_DIR/nxf" >/dev/null 2>&1 || true
export NXF_WORK="$TEAM_TMP_DIR/nxf"

# Setup output directory with timestamp and random ID
OUTPUT_DIR="$TEAM_TMP_DIR/${RANDOM_ID}"
mkdir -p "$OUTPUT_DIR"
chmod -R g+w "$OUTPUT_DIR" >/dev/null 2>&1 || true
cd "$OUTPUT_DIR"

# Run Nextflow process with the sample file
echo "Running Nextflow process for samples listed in: $SAMPLE_FILE"
nextflow run cellgeni/nf-irods-to-fastq -r main main.nf \
  --findmeta "$SAMPLE_FILE" \
  --publish_dir "$OUTPUT_DIR"

chmod -R g+w "$OUTPUT_DIR" >/dev/null 2>&1 || true
