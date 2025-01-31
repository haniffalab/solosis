#!/bin/bash
# submit.sh - Environment setup for imeta-report command   using 

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
CPU=2
MEM=3000
QUEUE="small"
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
OUTPUT_DIR="${TEAM_SAMPLE_DATA_DIR}/\$SAMPLE/cellranger"

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

####################################################

##find cellranger outputs
# Find the line that matches these values and output it in CSV format
imeta qu -C -z /seq/illumina sample = \$SAMPLE_IDS | \
grep "^collection: " | \
sed 's/^collection: //' > \$OUTPUT_DIR/\$SAMPLE/cellranger_path.csv

# Check if cellranger_path.csv is empty
if [ -s cellranger_path.csv ]; then
  cellranger_avail="yes"
else
  cellranger_avail="no"
fi

##find fastq/cram files
imeta qu -d -z /seq sample = \$SAMPLE_IDS | \
grep "^collection: " | \
sed 's/^collection: //' > \$OUTPUT_DIR/\$SAMPLE/cram_path.csv

# Check if cram_path.csv is empty
if [ -s cram_path.csv ]; then
  cram_avail="yes"
else
  cram_avail="no"
fi

# Check if cram_path.csv is empty
if [ -s cellranger_path.csv ] || [ -s cram_path.csv ]; then
  irods_avail="yes"
else
  irods_avail="no"
fi

# Confirm the saved cellranger output
num_paths=\$(wc -l cellranger_path.csv)
echo "Saved \$num_paths matching path(s) to \$OUTPUT_DIR/\$SAMPLE/cellranger_path.csv."

# Confirm the saved cellranger output
num_paths=\$(wc -l cram_path.csv)
echo "Saved \$num_paths matching path(s) to \$OUTPUT_DIR/\$SAMPLE/cram_path.csv."

# Number of sample IDs
num_samples=$(echo "\$SAMPLE_IDS" | tr ',' '\n' | wc -l)
#echo "\$num_samples sample(s) provided."


# Array of data
data=("\$SAMPLE_IDS \$irods_avail \$cram_avail \$cellranger_avail ")

# Define headers
printf "%-15s %-10s %-10s %-10s\n" "Samples" "irods" "cram" "cellranger"
printf "%-15s %-10s %-10s %-10s\n" "---------" "-------" "-------" "-------"

# Loop through data
for row in "${data[@]}"; do
    printf "%-15s %-10s %-10s %-10s\n" $row
done > irods_report.txt

EOF