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

# Check if at least 6 arguments are provided
if [ "$#" -lt 6 ]; then
  echo "Usage: $0 <sample_id> <output_dir> <fastq_dir> <version> <cpu> <mem> [--no-bam]" >&2
  exit 1
fi

# Assign command-line arguments to variables
SAMPLE_ID="$1"
OUTPUT_DIR="$2"
FASTQ_DIR="$3"
VERSION="$4"
CPU="$5"
MEM="$6"
BAM_FLAG=""  # Default to generating BAM files
REF="/software/cellgen/cellgeni/refdata_10x/refdata-gex-GRCh38-2024-A"

# Handle optional --no-bam flag (disables BAM file generation)
if [ "$7" == "--no-bam" ]; then
  BAM_FLAG="--no-bam"
fi

# Load Cell Ranger ARC module (make sure the version is correct)
if ! module load cellgen/cellranger/"$VERSION"; then
  echo "Failed to load Cell Ranger version $VERSION" >&2
  exit 1
fi

# Ensure output directory exists and create it if not
mkdir -p "$OUTPUT_DIR"
cd "$OUTPUT_DIR"

echo "Running Cell Ranger count for sample: $SAMPLE_ID"
echo "Output directory: $OUTPUT_DIR"
echo "FASTQ directory: $FASTQ_DIR"
echo "Cell Ranger version: $VERSION"
echo "Using $CPU CPU cores and $(($MEM / 1000)) GB memory"
[ -n "$BAM_FLAG" ] && echo "BAM output is disabled"

# Run Cell Ranger count
cellranger count \
    --id="$SAMPLE_ID" \
    --fastqs="$FASTQ_DIR" \
    --transcriptome="$REF" \
    --sample="$SAMPLE_ID" \
    --localcores="$CPU" \
    --localmem="$(($MEM / 1000))" \
    $BAM_FLAG

chmod -R g+w "$OUTPUT_DIR"
echo "Cell Ranger count completed for sample: $SAMPLE_ID"
