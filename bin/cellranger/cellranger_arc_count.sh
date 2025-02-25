#!/bin/bash
# cellranger_count.sh - Run Cell Ranger count for a given sample

# Usage:
#   ./cellranger_count.sh <sample_id> <output_dir> <fastq_dir> <version> <cpu> <mem> [--no-bam]
#
# Parameters:
#   <sample_id>   - Sample ID to process.
#   <output_dir>  - Path to store Cell Ranger output.
#   <fastq_dir>   - Path to FASTQ files.
#   <version>     - Version of Cell Ranger to use (e.g., "7.2.0").
#   <cpu>         - Number of CPU cores.
#   <mem>         - Memory in MB.
#   --no-bam      - Optional flag to disable BAM file generation.

set -e  # Exit immediately if a command fails

# Ensure at least 6 arguments are provided
if [ "$#" -lt 6 ]; then
  echo "Usage: $0 <sample_id> <output_dir> <fastq_dir> <version> <cpu> <mem> [--no-bam]" >&2
  exit 1
fi

# Assign command-line arguments to variables
ID="$1"
OUTPUT_DIR="$2"
LIBRARIES_PATH="$3"
VERSION="$4"
CPU="$5"
MEM="$6"
BAM_FLAG=""
REF="/software/cellgen/cellgeni/refdata-cellranger-arc-GRCh38-2020-A-2.0.0"

# Handle optional --no-bam flag
if [ "$7" == "--no-bam" ]; then
  BAM_FLAG="--no-bam"
fi

# Load Cell Ranger ARC module
if ! module load cellgen/cellranger-arc/"$VERSION"; then
  echo "Error: Failed to load cellranger-arc version $VERSION" >&2
  exit 1
fi

# Ensure required directories exist
mkdir -p "$OUTPUT_DIR"
cd "$OUTPUT_DIR"

echo "Running Cell Ranger ARC count for libraries file: $LIBRARIES_PATH"
echo "Output directory: $OUTPUT_DIR"
echo "Cell Ranger ARC version: $VERSION"
echo "Using $CPU CPU cores and $(($MEM / 1000)) GB memory"
[ -n "$BAM_FLAG" ] && echo "BAM output is disabled"

# Run Cell Ranger ARC count
cellranger-arc count \
    --id="$ID" \
    --libraries="$LIBRARIES_PATH" \
    --reference="$REF" \
    --localcores=$CPU \
    --localmem=$((MEM / 1000)) \
    $BAM_FLAG

echo "Cell Ranger ARC count completed for libraries file: $LIBRARIES_PATH"
