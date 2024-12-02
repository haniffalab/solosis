#!/bin/bash
# submit.sh - Environment setup for disk-usage

# Usage:
#   ./submit.sh 
#
# Parameters:
#   <change-this> - NOTHING ESSENTIAL

# Exit immediately if a command exits with a non-zero status
set -e

#removing for now.. chatGPT has a decent response to this though
# Ensure at least one argument is provided
#if [ "$#" -lt 1 ]; then
#  echo "Usage: $0" >&2
#  exit 1
#fi

nfs_overall=$(df -h /nfs/team298)


echo "printing nfs usage:" 
echo "$nfs_overall"