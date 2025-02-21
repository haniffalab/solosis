#!/bin/bash

set -e  # Exit on error



# Check if sample ID argument is provided
if [ -z "$1" ]; then
  echo "Error: No sample ID provided."
  echo "Usage: $0 <sample_id>"
  exit 1
fi

# Sample ID from the argument
SAMPLE=$1

if ! module load cellgen/irods; then
  echo "Error: Failed to load irods module" >&2
  exit 1
fi

# Find Cell Ranger outputs
echo "Finding Cell Ranger outputs for sample: $SAMPLE"
imeta qu -C -z /seq/illumina sample = "$SAMPLE" | \
grep "^collection: " | sed 's/^collection: //' > "cellranger_path.csv"

if [ $? -ne 0 ]; then
  echo "Error: Failed to retrieve Cell Ranger outputs for sample: $SAMPLE"
  exit 1
fi

echo "Cell Ranger outputs saved to cellranger_path.csv"

# Find FASTQ/CRAM files
echo "Finding FASTQ/CRAM files for sample: $SAMPLE"
imeta qu -d -z /seq sample = "$SAMPLE" | \
grep "^collection: " | sed 's/^collection: //' > "cram_path.csv"

if [ $? -ne 0 ]; then
  echo "Error: Failed to retrieve CRAM files for sample: $SAMPLE"
  exit 1
fi

echo "CRAM files saved to cram_path.csv"

exit 0



