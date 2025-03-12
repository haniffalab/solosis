#!/bin/bash
# cellranger_arc_count.sh - Run Cell Ranger ARC count for a given sample

# Usage:
#   ./cellranger_arc_count.sh <sample_id> <output_dir> <libraries_path> <version> <cpu> <mem> [--no-bam]
#
# Parameters:
#   <sample_id>      - Sample ID to process (unique identifier for the sample).
#   <output_dir>     - Path to store the Cell Ranger ARC output.
#   <libraries_path> - Path to the libraries file (CSV or TSV format).
#   <version>        - Version of Cell Ranger ARC to use (e.g., "2.0.2").
#   <cpu>            - Number of CPU cores to allocate.
#   <mem>            - Amount of memory in MB to allocate.
#   --no-bam         - Optional flag to disable BAM file generation (saves memory and disk space).

set -e  # Exit immediately if a command fails

# Check if at least 6 arguments are provided
if [ "$#" -lt 6 ]; then
  echo "Usage: $0 <sample_id> <output_dir> <libraries_path> <version> <cpu> <mem> [--no-bam]" >&2
  exit 1
fi

# Assign command-line arguments to variables
ID="$1"
OUTPUT_DIR="$2"
LIBRARIES_PATH="$3"
VERSION="$4"
CPU="$5"
MEM="$6"
BAM_FLAG=""  # Default to generating BAM files
REF="/software/cellgen/cellgeni/refdata-cellranger-arc-GRCh38-2020-A-2.0.0"  # Reference genome

# Handle optional --no-bam flag (disables BAM file generation)
if [ "$7" == "--no-bam" ]; then
  BAM_FLAG="--no-bam"
fi

# Load Cell Ranger ARC module (make sure the version is correct)
if ! module load cellgen/cellranger-arc/"$VERSION"; then
  echo "Error: Failed to load Cell Ranger ARC version $VERSION" >&2
  exit 1
fi

# Ensure output directory exists and create it if not
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

chmod -R g+w "$OUTPUT_DIR" || true
echo "Cell Ranger ARC count completed for libraries file: $LIBRARIES_PATH"
