#!/bin/bash
# cellbender.sh - Run Cellbender background removal for a given sample

# Usage:
#   ./cellbender.sh <sample_id> <output_dir> <cellranger_dir> <cpu> <mem> [--gpu <gpu_type>] [--total-droplets-included] [--expected-cells]
#
# Parameters:
#   <sample_id>       - Sample ID to process (unique identifier for the sample).
#   <output_dir>      - Path to store Cellbender output (processed data).
#   <cellranger_dir>  - Path to the Cell Ranger directory containing the raw matrix data.
#   <cpu>             - Number of CPU cores to allocate.
#   <mem>             - Amount of memory in MB to allocate.
#   --gpu <gpu_type>  - Optional flag to specify GPU type for processing (e.g., "NVIDIAA100_SXM4_80GB").
#   --total-droplets-included         - optional flag to choose a number that goes a few thousand barcodes into the 'empty droplet plateau' in UMI plot.
#   --expected-cells <expected_cells> - optional flag based on either the number of cells expected a priori from the experimental design.

set -e # Exit immediately if a command fails

# Check if at least 5 arguments are provided
if [ "$#" -lt 5 ]; then
  echo "Usage: $0 <sample_id> <output_dir> <cellranger_dir> [--cuda] <cpu> <mem> <queue> [--gpumem] [--gpu_type <gpu_type>] [--total-droplets-included <total_droplets_included>] [--expected-cells <expected_cells>]" >&2
  exit 1
fi

# Assign command-line arguments to variables
SAMPLE_ID="$1"
OUTPUT_DIR="$2"
CELLRANGER_DIR="$3"
CPU="$5"
MEM="$6"
# Optional flags
GPU_FLAG="$4" #$8 --cuda?
TOTAL_DROPLETS_FLAG="" # Default cellbender will calculate this
EXPECTED_CELLS_FLAG="" # Default cellbender will calculate this

# Parse optional arguments
shift 5
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
  *)
    echo "Warning: Unknown parameter $1 ignored"
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
echo "Using $CPU CPU cores and $(($MEM / 1000)) GB memory"
if [ -n "$GPU_FLAG" ]; then
  echo "GPU flag enabled: $GPU_FLAG"
else
  echo "GPU flag not enabled, using CPU"
fi

[ -n "$TOTAL_DROPLETS_FLAG" ] && echo "Total droplets included: $TOTAL_DROPLETS_FLAG" || echo "Cellbender will determine total droplets."
[ -n "$EXPECTED_CELLS_FLAG" ] && echo "Expected cells: $EXPECTED_CELLS_FLAG" || echo "Cellbender will determine expected cells."

# Run Cellbender
cellbender remove-background \
  "$GPU_FLAG" \
  --input "$CELLRANGER_DIR/raw_feature_bc_matrix.h5" \
  --output "$OUTPUT_DIR/$SAMPLE_ID-cb.h5" \
  "$TOTAL_DROPLETS_FLAG" \
  "$EXPECTED_CELLS_FLAG"
# Q="gpu-normal"
# GMEM=6000  # GPU memory
# DROPLETS=$2
# cellbender remove-background --cuda --input $VOY_DATA/$sample/cellranger/outs/raw_feature_bc_matrix.h5 --output $VOY_DATA/$sample/cellbender-results/$sample-cb.h5 --total-droplets-included $DROPLETS
# #BSUB -gpu "mode=shared:j_exclusive=no:gmem=${GMEM}:num=1:gmodel=NVIDIAA100_SXM4_80GB"

chmod -R g+w "$OUTPUT_DIR" >/dev/null 2>&1 || true
echo "Cellbender completed for sample: $SAMPLE_ID"
