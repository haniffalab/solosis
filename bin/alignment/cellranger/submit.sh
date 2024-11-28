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

# Load Cell Ranger module
if ! module load cellgen/cellranger/"$VERSION"; then
  echo "Error: Failed to load Cell Ranger version $VERSION" >&2
  exit 1
fi

# Configure paths and job parameters
TEAM_SAMPLE_DATA_DIR="/lustre/scratch126/cellgen/team298/data/samples"
TEAM_LOGS_DIR="$HOME/logs"
CPU=16
MEM=64000
QUEUE="normal"
GROUP="team298"
REF="/software/cellgen/cellgeni/refdata-gex-GRCh38-2024-A"

# Ensure logs directory exists
mkdir -p "$TEAM_LOGS_DIR"

# Convert comma-separated sample IDs into an array
IFS=',' read -r -a SAMPLES <<< "$SAMPLE_IDS"
NUM_SAMPLES=${#SAMPLES[@]}

# Submit an array job to LSF, with each task handling a specific sample
bsub -J "cellranger_array[1-$NUM_SAMPLES]" <<EOF
#!/bin/bash
#BSUB -o "$TEAM_LOGS_DIR/cellranger_%J_%I.out"   # Standard output with array job index
#BSUB -e "$TEAM_LOGS_DIR/cellranger_%J_%I.err"   # Standard error with array job index
#BSUB -n $CPU                                    # Number of CPU cores
#BSUB -M $MEM                                    # Memory limit in MB
#BSUB -R "span[hosts=1] select[mem>$MEM] rusage[mem=$MEM]" # Resource requirements
#BSUB -G $GROUP                                  # Group for accounting
#BSUB -q $QUEUE                                  # Queue name

# Determine the sample for the current task
SAMPLE_INDEX=\$((LSB_JOBINDEX - 1))
SAMPLE=${SAMPLES[$SAMPLE_INDEX]}

# Define paths for the current sample
FASTQ_PATH="${TEAM_SAMPLE_DATA_DIR}/\$SAMPLE/fastq"
OUTPUT_DIR="${TEAM_SAMPLE_DATA_DIR}/\$SAMPLE/cellranger/$VERSION"

# Create output directory if it does not exist
mkdir -p "\$OUTPUT_DIR"

# Check if Cell Ranger lock already exists for the sample
if [ -f "\${OUTPUT_DIR}/_lock" ]; then
  echo "Cell Ranger job is currently running or was interrupted for sample \${SAMPLE} in \${OUTPUT_DIR}." >&2
  exit 0
fi

# Check if Cell Ranger output already exists for the sample
if [ -f "\$OUTPUT_DIR/_invocation" ]; then
  echo "Cell Ranger output already exists for sample \${SAMPLE}. Skipping job." >&2
  exit 0
fi

# Change to the output directory to ensure all outputs are generated here
cd "\$OUTPUT_DIR"

# Run Cell Ranger 'count' for the sample
cellranger count \
    --id="\$SAMPLE" \
    --fastqs="\$FASTQ_PATH" \
    --transcriptome="$REF" \
    --sample="\$SAMPLE" \
    --localcores=$CPU \
    --localmem=$((MEM / 1000)) \
    $BAM_FLAG
EOF

echo "Submitted array job for $NUM_SAMPLES samples."
