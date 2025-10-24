#!/bin/bash
# cellranger_count.sh - Run Cell Ranger count for a given sample

# Usage:
#   ./cellranger_count.sh <sample_id> <output_dir> <fastq_dir> <version> <cpu> <mem> <time> [--no-bam] [--chemistry <str>]
#
# Parameters:
#   <sample_id>   - Sample ID to process.
#   <output_dir>  - Path to store Cell Ranger output.
#   <fastq_dir>   - Path to FASTQ files.
#   <version>     - Version of Cell Ranger to use (e.g., "7.2.0").
#   <cpu>         - Number of CPU cores.
#   <mem>         - Memory in MB.
#   <time>        - Time allocated to LSF job.
#   --no-bam      - Optional flag to disable BAM file generation.
#   --chemistry <value> - Optional chemistry of assay kit used.

set -e # Exit immediately if a command fails

# Check if at least 7 arguments are provided
if [ "$#" -lt 7 ]; then
	echo "Usage: $0 <sample_id> <output_dir> <fastq_dir> <version> <cpu> <mem> <time> [--no-bam] [--chemistry]" >&2
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
# Initialize optional flags
BAM_FLAG=""  # Default to generating BAM files
CHEMISTRY="" # Default should detect chemistry
# Define reference
REF="/software/cellgen/cellgeni/refdata_10x/refdata-gex-GRCh38-2024-A"
echo "Arguments received: $@"

# Convert version string (e.g. 9.0.1) to integer (901)
INT_VERSION=$(echo "$VERSION" | tr -d '.')

# Parse optional arguments
shift 7
while [[ "$#" -gt 0 ]]; do
	case "$1" in
	--chemistry)
		if [[ -n "$2" && "$2" != --* ]]; then
			CHEMISTRY="--chemistry $2"
			shift 2
		else
			echo "Error: --chemistry requires a value (check options via --help)" >&2
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

# Load Cell Ranger ARC module (make sure the version is correct)
if ! module load cellgen/cellranger/"$VERSION"; then
	echo "Failed to load Cell Ranger version $VERSION" >&2
	exit 1
fi

# Ensure output directory exists and create it if not
mkdir -p "$OUTPUT_DIR"
chmod 2775 "$OUTPUT_DIR" >/dev/null 2>&1 || true
cd "$OUTPUT_DIR"

echo "Running Cell Ranger count for sample: $SAMPLE_ID"
echo "Output directory: $OUTPUT_DIR"
echo "FASTQ directory: $FASTQ_DIR"
echo "Cell Ranger version: $VERSION"
echo "Using $CPU CPU cores and $(($MEM / 1000)) GB memory"
# Debugging
[ -n "$BAM_FLAG" ] && echo "BAM output is disabled"
[ -n "$CHEMISTRY" ] && echo "Using chemistry option: $CHEMISTRY"

# Run Cell Ranger count
cellranger count \
	--id="$SAMPLE_ID" \
	--fastqs="$FASTQ_DIR" \
	--transcriptome="$REF" \
	--sample="$SAMPLE_ID" \
	--localcores="$CPU" \
	--localmem="$(($MEM / 1000))" \
	"$BAM_FLAG" \
	"$CHEMISTRY"

chmod -R g+w "$OUTPUT_DIR" >/dev/null 2>&1 || true
echo "Cell Ranger count completed for sample: $SAMPLE_ID"

log_file="$OUTPUT_DIR/$SAMPLE_ID/_log"
if grep -q "Pipestance completed successfully!" "$log_file"; then
	echo "CellRanger completed successfully for sample: $SAMPLE_ID"
else
	echo "CellRanger incomplete or not found for sample: $SAMPLE_ID."
fi
