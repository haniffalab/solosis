#!/bin/bash
# scanpy/submit.sh - Run Scanpy notebook for a given sample

# REQUIREMENTS- running `iget-cellranger` cmd first.

# Usage:
#   ./submit.sh <sample_id> <output_dir> <cellranger_dir> <version> <cpu> <mem> <time> [--sample_basedir <path>] 
#
# Parameters:
#   <sample_id>         - Sample ID to process.
#   <output_dir>        - Path to store scanpy output.
#   <fastq_dir>         - Path to Cell Ranger outputs.
#   <cpu>               - Number of CPU cores.
#   <mem>               - Memory in MB.
#   <time>              - Time allocated to LSF job.
#   --sample_basedir <path>    - Optional flag to store scanpy outputs in an alternative location to <output_dir> .

set -e # Exit immediately if a command fails

module load cellgen/conda
conda_env="/software/cellgen/team298/shared/envs/hlb-conda/rna"

# Check if at least 7 arguments are provided
if [ "$#" -lt 6 ]; then
  echo "Usage: $0 <sample_id> <output_dir> <cellranger_dir> <cpu> <mem> <time> [--sample_basedir] " >&2
  exit 1
fi

# Assign command-line arguments to variables
SAMPLE_ID="$1"
OUTPUT_DIR="$2"
CELLRANGER_DIR="$3"
CPU="$4"
MEM="$5"
TIME="$6"
# Initialize optional flags

#### hardcoded for now ####
sample_basedir="/lustre/scratch124/cellgen/haniffa/data/samples"  # Default to use <outout_dir>
solosis_dir="/nfs/users/nfs_l/lg28/repos/solosis"
## will need to add conditional statemnt from replacing <output_dir> with --sample_basedir

echo "Arguments received: $@"

# Ensure output directory exists and create it if not
mkdir -p "$OUTPUT_DIR"
cd "$OUTPUT_DIR"

echo "Running scanpy notebook for sample: $SAMPLE_ID"
echo "Output directory: $OUTPUT_DIR"
echo "cellranger directory: $CELLRANGER_DIR"
echo "Using $CPU CPU cores and $(($MEM / 1000)) GB memory"

# run the papermill command
cmd="conda activate $conda_env &&  \
    papermill $solosis_dir/notebooks/sc_base1.ipynb \
    $OUTPUT_DIR/${SAMPLE_ID}_${SAMPLE_ID}.ipynb  \
    -p samples_database '${sample_basedir}' \
    -p sample_name $SAMPLE_ID \
    -p sample_id $SAMPLE_ID \
    -p cellranger_folder cellranger/${CELLRANGER_DIR##*/} \
    --log-output"

echo "Executing papermill command:"
echo "$cmd"
eval "$cmd"

chmod -R g+w "$OUTPUT_DIR" >/dev/null 2>&1 || true
echo "Scanpy notebook completed for sample: $SAMPLE_ID"