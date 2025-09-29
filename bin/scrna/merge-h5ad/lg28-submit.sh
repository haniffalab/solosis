#!/bin/bash
# scanpy/submit.sh - Run merge-h5ad notebook for a given list of samples

# REQUIREMENTS- running `scanpy` cmd first.

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