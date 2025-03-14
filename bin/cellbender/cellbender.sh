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

set -e  # Exit immediately if a command fails

# Check if at least 5 arguments are provided
if [ "$#" -lt 5 ]; then
  echo "Usage: $0 <sample_id> <output_dir> <cellranger_dir> <cpu> <mem> [--gpu <gpu_type>] [--total-droplets-included <total_droplets_included>] [--expected-cells <expected_cells>]" >&2
  exit 1
fi

# Assign command-line arguments to variables
SAMPLE_ID="$1"
OUTPUT_DIR="$2"
CELLRANGER_DIR="$3"
CPU="$4"
MEM="$5" 
GPU_FLAG="" #$8 --cuda?
TOTAL_DROPLETS_FLAG="" #by default cellbender will calculate this 
EXPECTED_CELLS_FLAG=""

# Handle optional arguments for GPU
# 

# Handle optional --total-droplets-included flag (defines specifc value of total droplets included)
#if [ "$7" == "--total-droplets-included" ]; then
#  TOTAL_DROPLETS_FLAG="--total-droplets-included"
#fi

# Handle optional --expected-cells flag (defines specifc value of expected cells)
#if [ "$8" == "--expected-cells" ]; then
#  EXPECTED_CELLS_FLAG="--expected-cells"
#fi
# Parsing additional flags from the arguments
for i in "$@"; do
  case $i in
    --gpu)
      GPU_FLAG="--gpu $5"
      shift
      ;;
    --total-droplets-included)
      TOTAL_DROPLETS_FLAG="--total-droplets-included $5"
      shift
      ;;
    --expected-cells)
      EXPECTED_CELLS_FLAG="--expected-cells $6"
      shift
      ;;
    *)
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

if [ -n "$TOTAL_DROPLETS_FLAG" ]; then
  echo "total droplets value for sample: $TOTAL_DROPLETS_FLAG"
else
  echo "cellbender calculating reasonable total droplets value."
fi

if [ -n "$EXPECTED_CELLS_FLAG" ]; then
  echo "expected cell count for sample: $EXPECTED_CELLS_FLAG"
else
  echo "cellbender calculating reasonable expected cell count."
fi


# Run Cellbender background removal (adjusting command based on optional GPU flag)
cellbender remove-background \
     $GPU_FLAG \
     --input "$CELLRANGER_DIR/raw_feature_bc_matrix.h5" \
     --output "$OUTPUT_DIR/$SAMPLE_ID-cb.h5" \
     $TOTAL_DROPLETS_FLAG \
     $EXPECTED_CELLS_FLAG
# Q="gpu-normal"
# GMEM=6000  # GPU memory
# DROPLETS=$2
# cellbender remove-background --cuda --input $VOY_DATA/$sample/cellranger/outs/raw_feature_bc_matrix.h5 --output $VOY_DATA/$sample/cellbender-results/$sample-cb.h5 --total-droplets-included $DROPLETS
# #BSUB -gpu "mode=shared:j_exclusive=no:gmem=${GMEM}:num=1:gmodel=NVIDIAA100_SXM4_80GB"

chmod -R g+w "$OUTPUT_DIR"
echo "Cellbender completed for sample: $SAMPLE_ID"