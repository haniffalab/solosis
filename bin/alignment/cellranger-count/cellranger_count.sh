#!/bin/bash
# submit.sh - Array job submission for Cell Ranger using LSF

# Usage:
#   ./submit.sh <sample_ids> <version> [--no-bam]
#
# Parameters:
#   <sample_ids> - Comma-separated list of sample IDs to process.
#   <version> - Version of Cell Ranger to use (e.g., "7.2.0").
#   --no-bam - Optional flag to exclude BAM output.

# Exit immediately if a command exits with a non-zero status
set -e

# Ensure at least two arguments are provided
if [ "$#" -lt 2 ]; then
  echo "Usage: $0 <sample_ids> <version> [--no-bam]" >&2
  exit 1
fi

# Assign command-line arguments to variables
SAMPLE_IDS="$1"
VERSION="$2"
BAM_FLAG=""
if [ "$3" == "--no-bam" ]; then
  BAM_FLAG="--no-bam"
fi

# Verify that the sample list is not empty
if [ -z "$SAMPLE_IDS" ]; then
  echo "Error: No samples provided." >&2
  exit 1
fi

# Determine the sample for the current task
SAMPLE=\${SAMPLES[\$((LSB_JOBINDEX - 1))]}

# Debug: output sample for current task
echo "Processing sample \$SAMPLE with index \$LSB_JOBINDEX"


# Define paths for the current sample
FASTQ_PATH="${TEAM_DATA_DIR}/samples/\$SAMPLE/fastq"
OUTPUT_DIR="${TEAM_DATA_DIR}/samples/\$SAMPLE/cellranger/$VERSION"

echo "DEBUG: SAMPLE_INDEX=\$SAMPLE_INDEX"
echo "DEBUG: SAMPLE=\$SAMPLE"

# Create output directory if it does not exist
mkdir -p "$OUTPUT_DIR"
cd "$OUTPUT_DIR"
cellranger count \
    --id="$SAMPLE" \
    --fastqs="$FASTQ_PATH" \
    --transcriptome="$REF" \
    --sample="$SAMPLE" \
    --localcores=$CPU \
    --localmem=$((MEM / 1000)) \
    $BAM_FLAG


