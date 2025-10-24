#!/bin/bash
# cellranger_vdj.sh - Run Cell Ranger vdj for a given sample

# Usage:
#   ./cellranger_vdj.sh <sample_id> <output_dir> <fastq_dir> <version> <cpu> <mem>
#
# Parameters:
#   <sample_id>   - Sample ID to process.
#   <output_dir>  - Path to store Cell Ranger output.
#   <fastq_dir>   - Path to FASTQ files.
#   <version>     - Version of Cell Ranger to use (e.g., "7.2.0").
#   <cpu>         - Number of CPU cores.
#   <time>        - Time allocated to LSF job.
#   <mem>         - Memory in MB.

set -e # Exit immediately if a command fails

# Check if at least 6 arguments are provided
if [ "$#" -lt 7 ]; then
	echo "Usage: $0 <sample_id> <output_dir> <fastq_dir> <version> <cpu> <mem> <time>" >&2
	exit 1
fi

# Assign command-line arguments to variables
SAMPLE_ID="$1"
OUTPUT_DIR="$2"
FASTQ_DIR="$3"
VERSION="$4"
CPU="$5"
MEM="$6"
TIME="$7"
REF="/software/cellgen/cellgeni/refdata_10x/refdata-cellranger-vdj-GRCh38-alts-ensembl-7.1.0"

# Load Cell Ranger module (make sure the version is correct)
if ! module load cellgen/cellranger/"$VERSION"; then
	echo "Failed to load Cell Ranger version $VERSION" >&2
	exit 1
fi

# Ensure output directory exists and create it if not
mkdir -p "$OUTPUT_DIR"
chmod 2775 "$OUTPUT_DIR" >/dev/null 2>&1 || true
cd "$OUTPUT_DIR"

echo "Running Cell Ranger VDJ for sample: $SAMPLE_ID"
echo "Output directory: $OUTPUT_DIR"
echo "FASTQ directory: $FASTQ_DIR"
echo "Cell Ranger version: $VERSION"
echo "Using $CPU CPU cores and $(($MEM / 1000)) GB memory"

# Run Cell Ranger vdj
cellranger vdj \
	--id="$SAMPLE_ID" \
	--fastqs="$FASTQ_DIR" \
	--reference="$REF" \
	--sample="$SAMPLE_ID" \
	--localcores="$CPU" \
	--localmem="$(($MEM / 1000))"

chmod -R g+w "$OUTPUT_DIR" >/dev/null 2>&1 || true
echo "Cell Ranger VDJ completed for sample: $SAMPLE_ID"
