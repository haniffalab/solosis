#!/bin/bash
# command.sh - Run command for a given sample

# Use cellranger-count command as working example.

# Usage:
#   ./command.sh <sample_id> <output_dir> ...
#
# Parameters:
#   <sample_id>   - Sample ID to process.
#   <output_dir>  - Path to store output.
#   --optional      - Optional flag.

set -e  # Exit immediately if a command fails

# Check if at least 3 arguments are provided
if [ "$#" -lt 3 ]; then
  echo "Usage: $0 <sample_id> <output_dir> [--optional]" >&2
  exit 1
fi

# Assign command-line arguments to variables
SAMPLE_ID="$1"
OUTPUT_DIR="$2"
OPTIONAL=""  # Default arg

# Handle optional flag 
if [ "$3" == "--optional" ]; then
  OPTIONAL="--optional"
fi

# If the command uses a module available on Farm 
# Load module 
if ! module load MODULE; then
  echo "Failed to load MODULE" >&2
  exit 1
fi

# Ensure output directory exists and create it if not
mkdir -p "$OUTPUT_DIR"
cd "$OUTPUT_DIR"


# DEBUGGING information 
echo "Running command for sample: $SAMPLE_ID"
echo "Output directory: $OUTPUT_DIR"


# Run command 
echo "hello world"
