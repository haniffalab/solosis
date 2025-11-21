#!/bin/bash
# submit.sh - Environment setup for pull-fastq processing using Nextflow

# Usage:
#   ./submit.sh <sample_file>
#
# Parameters:
#   <sample_file> - Path to a file containing sample IDs, one per line.

# Exit immediately if a command exits with a non-zero status
set -e

# Ensure exactly one argument is provided
if [ "$#" -ne 1 ]; then
  echo "Usage: $0 <sample_file>" >&2
  exit 1
fi

# Assign command-line argument to variable
SAMPLE_FILE="$1"

# Verify that the file exists and is not empty
if [ ! -f "$SAMPLE_FILE" ] || [ ! -s "$SAMPLE_FILE" ]; then
  echo "Error: Sample file '$SAMPLE_FILE' does not exist or is empty." >&2
  exit 1
fi

# Load necessary modules
module load cellgen/nextflow/24.10.0
module load cellgen/irods
module load cellgen/singularity
module load python-3.11.6

# Setup Nextflow work directory
mkdir -p "$TEAM_TMP_DIR/nxf"
chmod -R g+w "$TEAM_TMP_DIR/nxf" >/dev/null 2>&1 || true
export NXF_WORK="$TEAM_TMP_DIR/nxf"

# Setup output directory
mkdir -p "$TEAM_TMP_DIR/fastq"
chmod -R g+w "$TEAM_TMP_DIR/fastq" >/dev/null 2>&1 || true
cd "$TEAM_TMP_DIR/fastq"

# Run Nextflow process with the sample file
echo "Running Nextflow process for samples listed in: $SAMPLE_FILE"
nextflow run cellgeni/nf-irods-to-fastq -r main main.nf \
  --findmeta "$SAMPLE_FILE" \
  --cram2fastq \
  --publish_dir "$TEAM_TMP_DIR/fastq" \
  --resume

# Read sample IDs from file and process each
while IFS= read -r SAMPLE; do
  [ -z "$SAMPLE" ] && continue # Skip empty lines
  SAMPLE_DIR="${TEAM_DATA_DIR}/samples/${SAMPLE}/fastq"

  # Create sample directory if it does not exist
  mkdir -p "$SAMPLE_DIR"

  # Assumption: The FASTQ files for each sample are named with the sample ID as the prefix.
  # For example:
  # Sample ID: HCA_SkO13919076
  # Associated FASTQ files would be named as:
  # HCA_SkO13919076_S1_L001_R1_001.fastq.gz
  # HCA_SkO13919076_S1_L001_R2_001.fastq.gz
  # HCA_SkO13919076_S1_L001_I1_001.fastq.gz
  # HCA_SkO13919076_S1_L001_I2_001.fastq.gz
  #
  # Where:
  # - The filename starts with the sample ID (e.g., HCA_SkO13919076).
  # - The filenames follow the CellRanger convention, with S (sample), L (lane), R (read), and I (index) information.

  # Move FASTQ files into the respective sample directory
  echo "Moving FASTQ files for sample $SAMPLE to $SAMPLE_DIR"
  mv "$TEAM_TMP_DIR/fastq/${SAMPLE}"* "$SAMPLE_DIR"/
  chmod -R g+w "$SAMPLE_DIR" >/dev/null 2>&1 || true
done <"$SAMPLE_FILE"
