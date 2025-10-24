#!/bin/bash
# cellranger_count.sh - Run Cell Ranger count for a given sample

# Usage:
#   ./cellranger_count.sh <sample_id> <output_dir> <fastq_dir> <version> <cpu> <mem> <time> [--no-bam] [--chemistry <str>]

set -euo pipefail # Exit on errors, undefined variables, and failed pipelines

# Check if at least 7 arguments are provided
if [ "$#" -lt 7 ]; then
	echo "Usage: $0 <sample_id> <output_dir> <fastq_dir> <version> <cpu> <mem> <time> [--no-bam] [--chemistry]" >&2
	exit 1
fi

# Required arguments
SAMPLE_ID="$1"
OUTPUT_DIR="$2"
FASTQ_DIR="$3"
VERSION="$4"
CPU="$5"
MEM="$6"
TIME="$7"

# Optional flags
BAM_FLAG=""
CHEMISTRY=""

# Reference genome
REF="/software/cellgen/cellgeni/refdata_10x/refdata-gex-GRCh38-2024-A"

echo "Arguments received: $@"

# Convert version string (e.g., 9.0.1 to 901)
INT_VERSION=$(echo "$VERSION" | tr -d '.')

# Parse optional arguments
shift 7
while [[ "$#" -gt 0 ]]; do
	case "$1" in
	--chemistry)
		if [[ -n "${2:-}" && "$2" != --* ]]; then
			CHEMISTRY="--chemistry $2"
			shift 2
		else
			echo "Error: --chemistry requires a value" >&2
			exit 1
		fi
		;;
	--no-bam)
		if [ "$INT_VERSION" -ge 901 ]; then
			BAM_FLAG="--create-bam false"
		else
			BAM_FLAG="--no-bam"
		fi
		shift
		;;
	*)
		echo "Warning: Unknown parameter '$1' ignored." >&2
		shift
		;;
	esac
done

# Load Cell Ranger module
if ! module load cellgen/cellranger/"$VERSION"; then
	echo "Failed to load Cell Ranger version $VERSION" >&2
	exit 1
fi

# Ensure output directory exists
mkdir -p "$OUTPUT_DIR"
chmod 2775 "$OUTPUT_DIR" >/dev/null 2>&1 || true
cd "$OUTPUT_DIR"

# Validate memory: must be at least 1 GB
MEM_GB=$((MEM / 1000))
if [ "$MEM_GB" -lt 1 ]; then
	MEM_GB=1
fi

echo "Running Cell Ranger count for sample: $SAMPLE_ID"
echo "Output directory: $OUTPUT_DIR"
echo "FASTQ directory: $FASTQ_DIR"
echo "Cell Ranger version: $VERSION"
echo "Using $CPU CPU cores and $MEM_GB GB memory"

[ -n "$BAM_FLAG" ] && echo "BAM output is disabled"
[ -n "$CHEMISTRY" ] && echo "Using chemistry option: $CHEMISTRY"

# Build command array to avoid empty argument issues
ARGS=(
	--id="$SAMPLE_ID"
	--fastqs="$FASTQ_DIR"
	--transcriptome="$REF"
	--sample="$SAMPLE_ID"
	--localcores="$CPU"
	--localmem="$MEM_GB"
)

[ -n "$BAM_FLAG" ] && ARGS+=($BAM_FLAG)
[ -n "$CHEMISTRY" ] && ARGS+=($CHEMISTRY)

# Run Cell Ranger count
cellranger count "${ARGS[@]}"

# Fix permissions
chmod -R g+w "$OUTPUT_DIR" >/dev/null 2>&1 || true
echo "Cell Ranger count completed for sample: $SAMPLE_ID"

# Check log file
log_file="$OUTPUT_DIR/$SAMPLE_ID/_log"
if [ -f "$log_file" ] && grep -q "Pipestance completed successfully!" "$log_file"; then
	echo "Cell Ranger completed successfully for sample: $SAMPLE_ID"
else
	echo "Cell Ranger incomplete or log not found for sample: $SAMPLE_ID."
fi
