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

# Create a temporary file for sample IDs in CSV format
TMP_SAMPLE_FILE=$(mktemp /tmp/sample_ids.XXXXXX.csv)

# Convert comma-separated list to a file with one sample ID per line
IFS=',' read -r -a SAMPLES <<< "$SAMPLE_IDS"
for SAMPLE in "${SAMPLES[@]}"; do
  echo "$SAMPLE" >> "$TMP_SAMPLE_FILE"
done

# Load necessary modules
MODULES=("irods" "conda" "nextflow" "singularity")
for MODULE in "${MODULES[@]}"; do
  if ! module load cellgen/"$MODULE"; then
    echo "Error: Failed to load $MODULE module" >&2
    exit 1
  fi
done

# Configure paths and environment variables
export NXF_WORK="/lustre/scratch126/cellgen/team298/data/tmp"
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

cd "$OUTPUT_DIR"
# Run pull-fastq Nextflow process with the sample file
echo "Running Nextflow process for samples listed in: $TMP_SAMPLE_FILE"
nextflow run cellgeni/nf-irods-to-fastq -r main main.nf \
    --findmeta "$TMP_SAMPLE_FILE" \
    --cram2fastq \
    --publish_dir "$OUTPUT_DIR" \
    --resume

# Loop through each sample and move the FASTQ files to their respective directories
for SAMPLE in "${SAMPLES[@]}"; do
  SAMPLE_DIR="${TEAM_SAMPLE_DATA_DIR}/${SAMPLE}/fastq"
  
  # Create the sample directory if it does not exist
  mkdir -p "$SAMPLE_DIR"
  
  # Assumption: The FASTQ files for each sample are named with the sample ID as the prefix.
  # For example: 
  # Sample ID: HCA_SkO13919076
  # Associated FASTQ files would be named as:
  # HCA_SkO13919076_S1_L001_R1_001.fastq.gz
  # HCA_SkO13919076_S1_L001_R2_001.fastq.gz
  # HCA_SkO13919076_S1_L001_I1_001.fastq.gz
  # HCA_SkO13919076_S1_L001_I2_001.fastq.gz
  #
  # Where:
  # - The filename starts with the sample ID (e.g., HCA_SkO13919076).
  # - The filenames follow the CellRanger convention, with S (sample), L (lane), R (read), and I (index) information.

  # Move FASTQ files into the respective sample directory
  echo "Moving FASTQ files for sample $SAMPLE to $SAMPLE_DIR"
  mv ${OUTPUT_DIR}/${SAMPLE}* "$SAMPLE_DIR"/
done

# Clean up the temporary sample file after Nextflow completes
rm -f "$TMP_SAMPLE_FILE"

echo "All samples processed and FASTQ files moved to respective directories."
