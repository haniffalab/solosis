#!/bin/bash
# submit.sh - Array job submission for pull-fastq using LSF

# Usage:
#   ./submit.sh <sample_ids>
#
# Parameters:
#   <sample_ids> - Comma-separated list of sample IDs to process.

# Exit immediately if a command exits with a non-zero status
set -e

# Ensure at least 1 argument is provided
if [ "$#" -lt 1 ]; then
  echo "Usage: $0 <sample_ids>" >&2
  exit 1
fi

# Assign command-line arguments to variables
SAMPLE_IDS="$1"

# Verify that the sample list is not empty
if [ -z "$SAMPLE_IDS" ]; then
  echo "Error: No samples provided." >&2
  exit 1
fi

# Load irods module
if ! module load cellgen/irods; then
  echo "Error: Failed to load irods version " >&2
  exit 1
fi
# Load conda module
if ! module load cellgen/conda; then
  echo "Error: Failed to load conda version " >&2
  exit 1
fi
# Load nextflow module
if ! module load cellgen/nextflow; then
  echo "Error: Failed to load nextflow version " >&2
  exit 1
fi
# Load singularity module
if ! module load cellgen/singularity; then
  echo "Error: Failed to load singularity version " >&2
  exit 1
fi
# Configure paths and job parameters
export NXF_WORK=$HOME
export LSB_DEFAULT_USERGROUP=team298
export PATH="/software/singularity/v3.10.0/bin:$PATH"
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
bsub -J "pullfastq_array[1-$NUM_SAMPLES]" <<EOF
#!/bin/bash
#BSUB -o "$TEAM_LOGS_DIR/pullfastq_%J_%I.out"   # Standard output with array job index
#BSUB -e "$TEAM_LOGS_DIR/pullfastq_%J_%I.err"   # Standard error with array job index
#BSUB -n $CPU                                    # Number of CPU cores
#BSUB -M $MEM                                    # Memory limit in MB
#BSUB -R "span[hosts=1] select[mem>$MEM] rusage[mem=$MEM]" # Resource requirements
#BSUB -G $GROUP                                  # Group for accounting
#BSUB -q $QUEUE     

# Determine the sample for the current task
SAMPLE_INDEX=\$((LSB_JOBINDEX - 1))
SAMPLE=${SAMPLES[$SAMPLE_INDEX]}

# Define paths for the current sample
OUTPUT_DIR="${TEAM_SAMPLE_DATA_DIR}/\$SAMPLE/fastq"

# Create output directory if it does not exist
mkdir -p "\$OUTPUT_DIR"

### do I still need to valid this if it's validated in pull-fastq.py?
# Check if FASTQ files already exists for the sample
if [ -f "\${OUTPUT_DIR}/*fastq.gz" ]; then
  echo "FASTQ files already exist  for sample \${SAMPLE} in \${OUTPUT_DIR}." >&2
  exit 0
fi

# Change to the output directory to ensure all outputs are generated here
cd "\$OUTPUT_DIR"

# Run pull-fastq for the sample
nextflow run cellgeni/nf-irods-to-fastq -r main main.nf \
	--findmeta "\$SAMPLE" \
	--cram2fastq \
	--publish_dir "\$OUTPUT_DIR"
EOF

echo "Submitted array job for $NUM_SAMPLES samples."

