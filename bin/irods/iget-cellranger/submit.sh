#!/bin/bash
# submit.sh - Environment setup for pull-cellranger processing using Nextflow

# Usage:
#   ./submit.sh <sample_ids>
#
# Parameters:
#   <sample_ids> - Comma-separated list of sample IDs to process.

# Exit immediately if a command exits with a non-zero status
set -e

# Ensure at least one argument is provided
if [ "$#" -lt 1 ]; then
  echo "Usage: $0 <sample_ids>" >&2
  exit 1
fi

# Assign command-line argument to variable
SAMPLE_IDS="$1"
retain_bam="$2"; shift
overwrite="$2"

# Verify that the sample list is not empty
if [ -z "$SAMPLE_IDS" ]; then
  echo "Error: No samples provided." >&2
  exit 1
fi

# Load irods module
if ! module load cellgen/irods; then
  echo "Error: Failed to load irods module" >&2
  exit 1
fi

# Configure paths
LSB_DEFAULT_USERGROUP="${LSB_DEFAULT_USERGROUP:?Environment variable LSB_DEFAULT_USERGROUP is not set. Please export it before running this script.}"
TEAM_DATA_DIR="${TEAM_DATA_DIR:?Environment variable TEAM_DATA_DIR is not set. Please export it before running this script.}"
TEAM_LOGS_DIR="${TEAM_LOGS_DIR:?Environment variable TEAM_LOGS_DIR is not set. Please export it before running this script.}"

# Ensure directories exists
mkdir -p "$TEAM_DATA_DIR"
mkdir -p "$TEAM_LOGS_DIR"

# Configure job parameters
CPU=2
MEM=3000
QUEUE="small"

# Convert comma-separated sample IDs into an array
IFS=',' read -r -a SAMPLES <<< "$SAMPLE_IDS"
NUM_SAMPLES=${#SAMPLES[@]}

# Submit an array job to LSF, with each task handling a specific sample
bsub -J "pull_cellranger_array[1-$NUM_SAMPLES]" <<EOF
#!/bin/bash
#BSUB -o "$TEAM_LOGS_DIR/pull_cellranger_%J_%I.out"   # Standard output with array job index
#BSUB -e "$TEAM_LOGS_DIR/pull_cellranger_%J_%I.err"   # Standard error with array job index
#BSUB -n $CPU                                    # Number of CPU cores
#BSUB -M $MEM                                    # Memory limit in MB
#BSUB -R "span[hosts=1] select[mem>$MEM] rusage[mem=$MEM]" # Resource requirements
#BSUB -G $LSB_DEFAULT_USERGROUP                                  # Group for accounting
#BSUB -q $QUEUE                                  # Queue name

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

# Define the output directory
OUTPUT_DIR="${TEAM_DATA_DIR}/samples/\$SAMPLE/cellranger"

################################

# Check if outputs already present
#if [ "\$(ls -A "\$OUTPUT_DIR")" ]; then
#    echo "Output directory '\$OUTPUT_DIR' already contains cellranger outputs. Exiting"
#    exit 0
#fi

# Create the output dir
mkdir -p "\$OUTPUT_DIR"

# Create the output directory if it doesn't exist
mkdir -p "\$OUTPUT_DIR"
cd "\$OUTPUT_DIR"

# Find the line that matches these values and output it in CSV format
imeta qu -C -z /seq/illumina sample = \$SAMPLE | \
grep "^collection: " | \
sed 's/^collection: //' > irods_path.csv

# Confirm the saved output
num_paths=\$(wc -l irods_path.csv)
echo "Saved \$num_paths matching path(s) to irods_path.csv."

# Read each line from irods_path.csv and use iget to pull files to the output dir
while IFS= read -r irods_path; do
    echo "Retrieving \$irods_path to \$OUTPUT_DIR"
    iget -r "\$irods_path" "\$OUTPUT_DIR"
done < irods_path.csv

# Confirmation message
echo "All Cellranger outputs for \$SAMPLE have been pulled to:"
echo "\$OUTPUT_DIR"

EOF



#unsure about confirmation message..
