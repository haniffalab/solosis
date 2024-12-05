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

# Configure paths and job parameters
TEAM_SAMPLE_DATA_DIR="/lustre/scratch126/cellgen/team298/data/samples"
TEAM_LOGS_DIR="$HOME/logs"
CPU=16
MEM=64000
QUEUE="normal"
GROUP="team298"

# Ensure logs directory exists
mkdir -p "$TEAM_LOGS_DIR"

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
#BSUB -G $GROUP                                  # Group for accounting
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
OUTPUT_DIR="${TEAM_SAMPLE_DATA_DIR}/\$SAMPLE/sanger-cellranger"

# Create the output directory if it doesn't exist
mkdir -p "\$OUTPUT_DIR"
cd "\$OUTPUT_DIR"

# Skip processing if the output directory already contains files
if [ "\$(ls -A "\$OUTPUT_DIR")" ]; then
    echo "Output directory '\$OUTPUT_DIR' already contains files. Skipping."
    exit 0
fi

# Fetch cellranger collections associated with the sample
collections=\$(imeta qu -C -z /seq/illumina sample = \$SAMPLE | grep "^collection: " | sed 's/^collection: //')

# Identify the highest-priority collection by sorting
filtered=\$(echo "\$collections" | grep -E "cellranger[0-9]+_count" | \
    awk '
    {
        match(\$0, /cellranger([0-9]+)_count_([0-9]+)_?([^_]+)?/, matches);
        version = matches[1];
        count = matches[2];
        extra = matches[3] ~ /^[0-9]+$/ ? matches[3] : -1;
        print version, count, extra, \$0;
    }' | sort -k1,1nr -k2,2nr -k3,3nr | head -n 1 | cut -d" " -f4-)

# Exit if no matching collections are found
if [ -z "\$filtered" ]; then
    echo "No matching paths found for sample \$SAMPLE."
    exit 1
fi

# Save the filtered path to CSV
echo "\$filtered" > irods_cellranger.csv

# Read each line from irods_path.csv and use iget to pull files to the output dir
# while IFS= read -r irods_path; do
#     echo "Retrieving \$irods_path to \$OUTPUT_DIR"
#     iget -KVf --progress -r "\$irods_path" "\$OUTPUT_DIR"
# done < irods_cellranger.csv

# Confirmation message
echo "All Cellranger outputs for \$SAMPLE have been pulled to:"
echo "\$OUTPUT_DIR"
EOF