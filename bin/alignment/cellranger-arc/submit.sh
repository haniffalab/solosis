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
if [ "$#" -lt 2 ]; then
  echo "Usage: $0 <libraries> <version> [--no-bam]" >&3
  exit 1
fi

# Assign command-line arguments to variables
TEMP_FILE="$1"
VERSION="$2"
BAM_FLAG=""
if [ "$3" == "--no-bam" ]; then
  BAM_FLAG="--no-bam"
fi

# Verify that the temp file exists
if [ ! -f "$TEMP_FILE" ]; then
  echo "Error: Temporary file $TEMP_FILE does not exist." >&2
  exit 1
fi

# Load Cell Ranger module
if ! module load cellgen/cellranger-arc/"$VERSION"; then
  echo "Error: Failed to load cellranger-arc version $VERSION" >&2
  exit 1
fi

# Configure paths
TEAM_DATA_DIR="${TEAM_DATA_DIR:?Environment variable TEAM_DATA_DIR is not set. Please export it before running this script.}"
TEAM_LOGS_DIR="${TEAM_LOGS_DIR:?Environment variable TEAM_LOGS_DIR is not set. Please export it before running this script.}"

# Ensure directories exists
mkdir -p "$TEAM_DATA_DIR/samples"
mkdir -p "$TEAM_LOGS_DIR"

# Configure job parameters
CPU=16
MEM=64000
QUEUE="normal"
GROUP="team298"
REF="/software/cellgen/cellgeni/refdata-cellranger-arc-GRCh38-2020-A-2.0.0"

# Read the libraries file and count entries
LIBRARIES=()
IDS=()
while IFS=',' read -r lib_path lib_id; do
  LIBRARIES+=("$lib_path")
  IDS+=("$lib_id")
done < "$TEMP_FILE"

NUM_LIBRARIES=${#LIBRARIES[@]}

# Submit an array job to LSF, with each task handling a specific sample
bsub -J "cellranger_arc_array[1-$NUM_LIBRARIES]" <<EOF
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
LIBRARIES=("${LIBRARIES[@]}")
IDS=("${IDS[@]}")

# Get the library path and ID for the current task
LIBRARY=\${LIBRARIES[\$((LSB_JOBINDEX - 1))]}
ID=\${IDS[\$((LSB_JOBINDEX - 1))]}

# Debug: output sample for current task
echo "Processing sample \$LIBRARY with index \$LSB_JOBINDEX"

# Define paths for the current sample
OUTPUT_DIR="${TEAM_DATA_DIR}/cellranger-arc-count/$ID"

echo "DEBUG: LIBRARY=\$LIBRARY"
echo "DEBUG: ID=\$ID"
echo "DEBUG: Output Directory \$OUTPUT_DIR"

# Create output directory if it does not exist
mkdir -p "\$OUTPUT_DIR"

# Check if Cell Ranger output already exists for the sample
if [ -f "\$OUTPUT_DIR/outs" ]; then
  echo "Cell Ranger output already exists for sample \${LIBRARY}. Skipping job." >&2
  exit 0
fi

# Change to the output directory to ensure all outputs are generated here
cd "\$OUTPUT_DIR"

# Run cellranger 'arc' for the sample
cellranger-arc count \
    --id="\$ID" \
    --libraries="\$LIBRARY" \
    --reference="$REF" \
    --localcores=$CPU \
    --localmem=$((MEM / 1000)) \
    $BAM_FLAG
EOF