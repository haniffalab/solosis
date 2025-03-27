#!/bin/bash
# cellbender.sh - Run Cellbender background removal for a given sample

# Usage:
#   ./cellbender.sh <sample_id> <output_dir> <cellranger_dir> [--gpu] [--total-droplets-included <value>] [--expected-cells <value>]
#
# Parameters:
#   <sample_id>       - Sample ID to process (unique identifier for the sample).
#   <output_dir>      - Path to store Cellbender output (processed data).
#   <cellranger_dir>  - Path to the Cell Ranger directory containing the raw matrix data.
#   --gpu             - Optional flag to enable GPU (--cuda).
#   --total-droplets-included <value> - Optional flag to specify droplet count.
#   --expected-cells <value> - Optional flag to specify expected cells count.

set -e # Exit on failure

# Check if at least 3 arguments are provided
if [ "$#" -lt 3 ]; then
  echo "Usage: $0 <sample_id> <output_dir> <cellranger_dir> [--gpu] [--total-droplets-included <value>] [--expected-cells <value>]" >&2
  exit 1
fi

# Assign required arguments
SAMPLE_ID="$1"
OUTPUT_DIR="$2"
CELLRANGER_DIR="$3"

# Initialize optional flags
GPU_FLAG=""
TOTAL_DROPLETS_FLAG=""
EXPECTED_CELLS_FLAG=""

# Parse optional arguments
shift 3
while [[ "$#" -gt 0 ]]; do
  case "$1" in
  --total-droplets-included)
    if [[ -n "$2" && "$2" != --* ]]; then
      TOTAL_DROPLETS_FLAG="--total-droplets-included $2"
      shift 2
    else
      echo "Error: --total-droplets-included requires a value" >&2
      exit 1
    fi
    ;;
  --expected-cells)
    if [[ -n "$2" && "$2" != --* ]]; then
      EXPECTED_CELLS_FLAG="--expected-cells $2"
      shift 2
    else
      echo "Error: --expected-cells requires a value" >&2
      exit 1
    fi
    ;;
  --gpu)
    GPU_FLAG="--cuda"
    shift
    ;;
  *)
    echo "Warning: Unknown parameter '$1' ignored." >&2
    shift
    ;;
  esac
done

# Load Cellbender module
if ! module load cellgen/cellbender/; then
  echo "Error: Failed to load Cellbender module" >&2
  exit 1
fi

# Ensure output directory exists
mkdir -p "$OUTPUT_DIR"
cd "$OUTPUT_DIR"

# Display job configuration
echo "Running Cellbender for sample: $SAMPLE_ID"
echo "Output directory: $OUTPUT_DIR"
echo "Cell Ranger directory: $CELLRANGER_DIR"
echo "GPU flag: ${GPU_FLAG:-Not enabled}"
echo "Total droplets: ${TOTAL_DROPLETS_FLAG:-Auto-detected}"
echo "Expected cells: ${EXPECTED_CELLS_FLAG:-Auto-detected}"

# Construct command
CELLBENDER_CMD=("cellbender remove-background"
  "--input \"$CELLRANGER_DIR/raw_feature_bc_matrix.h5\""
  "--output \"$OUTPUT_DIR/${USER}_$(date +%Y%m%d).h5\""
)
[ -n "$GPU_FLAG" ] && CELLBENDER_CMD+=("$GPU_FLAG")
[ -n "$TOTAL_DROPLETS_FLAG" ] && CELLBENDER_CMD+=("$TOTAL_DROPLETS_FLAG")
[ -n "$EXPECTED_CELLS_FLAG" ] && CELLBENDER_CMD+=("$EXPECTED_CELLS_FLAG")

# Print the command before execution
echo "Executing: ${CELLBENDER_CMD[*]}"

eval "${CELLBENDER_CMD[*]}"

chmod -R g+w "$OUTPUT_DIR" >/dev/null 2>&1 || true
echo "Cellbender completed for sample: $SAMPLE_ID"
