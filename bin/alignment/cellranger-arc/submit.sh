#!/bin/bash
# submit.sh - Array job submission for Cell Ranger using LSF

# Usage:
#   ./submit.sh <sample_ids> <version> [--no-bam]
#
# Parameters:
#   <sample_ids> - Comma-separated list of sample IDs to process.
#   <version> - Version of Cell Ranger to use (e.g., "7.2.0").

# Exit immediately if a command exits with a non-zero status
set -e

# Ensure at least two arguments are provided
if [ "$#" -lt 3 ]; then
  echo "Usage: $0 <sample_ids> <libraries> <version> [--no-bam]" >&3
  exit 1
fi

# Assign command-line arguments to variables
SAMPLE_IDS="$1"
LIBRARIES="$2"
VERSION="$3"
BAM_FLAG=""
if [ "$4" == "--no-bam" ]; then
  BAM_FLAG="--no-bam"
fi

# Verify that the sample list is not empty
if [ -z "$SAMPLE_IDS" ]; then
  echo "Error: No samples provided." >&2
  exit 1
fi

# Verify that the libraries file is not empty
if [ -z "$LIBRARIES" ]; then
  echo "Error: No libraries.csv provided." >&2
  exit 1
fi

# Load Cell Ranger module
if ! module load cellgen/cellranger-arc/"$VERSION"; then
  echo "Error: Failed to load cellranger-arc version $VERSION" >&2
  exit
fi

# Configure paths
TEAM_SAMPLE_DATA_DIR="${TEAM_SAMPLE_DATA_DIR:?Environment variable TEAM_SAMPLE_DATA_DIR is not set. Please export it before running this script.}"

# Ensure logs directory exists
TEAM_LOGS_DIR="$HOME/logs"
mkdir -p "$TEAM_LOGS_DIR"

# Configure job parameters
CPU=16
MEM=64000
QUEUE="normal"
GROUP="team298"
REF="/software/cellgen/cellgeni/refdata-cellranger-arc-GRCh38-2020-A-2.0.0"

# Convert comma-separated sample IDs into an array
IFS=',' read -r -a SAMPLES <<< "$SAMPLE_IDS"
NUM_SAMPLES=${#SAMPLES[@]}

#####
# HOW TO INSERT LIBRARIES, DOES IT NEED TO BE ITERATIVE?
#####

# Submit an array job to LSF, with each task handling a specific sample
bsub -J "cellranger_arc_array[1-$NUM_SAMPLES]" <<EOF
#!/bin/bash
#BSUB -o "$TEAM_LOGS_DIR/cellranger_arc_%J_%I.out"   # Standard output with array job index
#BSUB -e "$TEAM_LOGS_DIR/cellranger_arc_%J_%I.err"   # Standard error with array job index
#BSUB -n $CPU                                    # Number of CPU cores
#BSUB -M $MEM                                    # Memory limit in MB
#BSUB -R "span[hosts=1] select[mem>$MEM] rusage[mem=$MEM]" # Resource requirements
#BSUB -G $GROUP                                  # Group for accounting
#BSUB -q $QUEUE     

# Define the samples array inside the job script
################################################
# The array is redefined here because the job scheduler environment does
# not inherit the array from the parent script, so we re-split the 
# SAMPLE_IDS string into an array in each individual job.
IFS=',' read -r -a SAMPLES <<< "$SAMPLE_IDS"

# Determine the sample for the current task
SAMPLE=\${SAMPLES[\$((LSB_JOBINDEX - 1))]}

# Debug: output sample for current task
echo "Processing sample \$SAMPLE with index \$LSB_JOBINDEX"

# Define paths for the current sample
FASTQ_PATH="${TEAM_SAMPLE_DATA_DIR}/\$SAMPLE/fastq"
OUTPUT_DIR="${TEAM_SAMPLE_DATA_DIR}/\$SAMPLE/cellranger-arc/$VERSION"

echo "DEBUG: SAMPLE_INDEX=\$SAMPLE_INDEX"
echo "DEBUG: SAMPLE=\$SAMPLE"

# Create output directory if it does not exist
mkdir -p "\$OUTPUT_DIR"

# Check if Cell Ranger output already exists for the sample
if [ -f "\$OUTPUT_DIR/outs" ]; then
  echo "Cell Ranger output already exists for sample \${SAMPLE}. Skipping job." >&2
  exit 0
fi

# Change to the output directory to ensure all outputs are generated here
cd "\$OUTPUT_DIR"

# Run cellranger 'arc' for the sample
cellranger-arc count \
    --id="\$SAMPLE" \
    --libraries="$LIBRARIES" \
    --reference="$REF" \
    --localcores=16 \
    --localmem=60 \
    $BAM_FLAG
EOF