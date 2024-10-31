#!/bin/bash
# ---------------------------------------------------------------------------
# Cell Ranger LSF Array Job Submission Script
# ---------------------------------------------------------------------------
# This script submits an array job to the LSF cluster for processing multiple 
# samples using the Cell Ranger 'count' function. It handles module loading, 
# environment setup, and job array submission for parallel processing.
#
# Arguments:
#   $1 - Comma-separated list of sample IDs to be processed.
#   $2 - Version of Cell Ranger to use (e.g., 6.1.1).
#   $3 - BAM inclusion flag (set to "1" to include BAM output, or "0" to exclude).
#
# Description:
#   For each sample ID specified, this script submits an individual job within 
#   an LSF job array. Each job performs the following steps:
#   1. Loads the specified version of the Cell Ranger module.
#   2. Configures paths for temporary and sample data.
#   3. Uses Cell Ranger to process the sample, storing output in a dedicated 
#      directory. If requested, includes BAM output.
#   4. Logs are stored in the user's home directory under $HOME/logs.
#
# Requirements:
#   - LSF job scheduler.
#   - Appropriate Cell Ranger module available.
#   - Directory paths defined for temporary and sample data storage.
#
# Example usage:
#   ./submit.sh "sample1,sample2,sample3" 6.1.1 1
# ---------------------------------------------------------------------------
# Load the specified version of the Cell Ranger module
if ! module load cellgen/cellranger/$2; then
    echo "Error: Failed to load Cell Ranger version $2" >&2
    exit 1
fi

# Set environment variables for data directories (temporary and sample data)
export TEAM_SAMPLE_DATA_DIR="/lustre/scratch126/cellgen/team298/data/samples"
export TEAM_TMP_DATA_DIR="/lustre/scratch126/cellgen/team298/tmp"
mkdir -p "$HOME/logs"

# Define job parameters for the LSF job submission
GROUP="team298"                          # User group for the job
CPU=16                                   # Number of CPU cores requested
MEM=64000                                # Memory requested (in MB)
Q="normal"                               # Job queue
REF="/software/cellgen/cellgeni/refdata-gex-GRCh38-2020-A"  # Reference dataset path
samples_list=$1                          # Comma-separated list of sample IDs
include_bam_flag=$3                      # Flag for including BAM output

# Verify that the sample list is not empty
if [[ -z "$samples_list" ]]; then
  echo "Error: No samples provided." >&2
  exit 1
fi

# Configure the BAM flag based on input (default to excluding BAM)
bam_flag="--no-bam"
if [[ "$include_bam_flag" -eq "1" ]]; then
  bam_flag=""  # Remove flag if BAM output is requested
fi

# Convert the comma-separated sample list into an array
IFS=',' read -r -a samples_array <<< "$samples_list"

# Calculate the number of samples for the array job
total_jobs=${#samples_array[@]}

# Submit the array job to LSF
bsub <<EOF
#!/bin/bash
#BSUB -J cellranger_array[1-$total_jobs]%20  # Submit job array, limit to 20 concurrent jobs
#BSUB -o $HOME/logs/%J_%I.bsub.log           # Standard output log per job index
#BSUB -e $HOME/logs/%J_%I.bsub.err           # Standard error log per job index
#BSUB -n $CPU                                # Allocate specified CPU cores
#BSUB -M $MEM                                # Set memory limit (in MB)
#BSUB -R "span[hosts=1] select[mem>${MEM}] rusage[mem=${MEM}]"  # Resource allocation
#BSUB -G $GROUP                              # Specify job group
#BSUB -q $Q                                  # Set job queue

# Retrieve the sample ID for the current job array index
sample=\${samples_array[\$((LSB_JOBINDEX - 1))]}  # Array index adjusted for 0-based indexing

# Create output directory for the current sample and version
mkdir -p "$TEAM_SAMPLE_DATA_DIR/\$sample/cellranger/$2"

# Run Cell Ranger 'count' function for the specified sample
if ! cellranger count --id="\$sample" --fastqs="$TEAM_TMP_DATA_DIR/\$sample" --transcriptome="$REF" \
    --sample="\$sample" --localcores=$CPU --localmem=$((MEM / 1000)) --output-dir="$TEAM_SAMPLE_DATA_DIR/\$sample/cellranger/$2" $bam_flag; then
    echo "Error during Cell Ranger execution for sample \$sample" >&2
    exit 1
fi
EOF
