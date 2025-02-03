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

# Load irods module
if ! module load cellgen/irods; then
  echo "Error: Failed to load irods module" >&2
  exit 1
fi

# Configure paths
TEAM_DATA_DIR=/lustre/scratch126/cellgen/team298/data
OUTPUT_DIR="$TEAM_DATA_DIR/reports/storage/"
# Create the output dir
mkdir -p "$OUTPUT_DIR"

# lustre
#lfs quota -g team298 -h /lustre/scratch126
lustre_size=$(lfs quota -g team298 -h /lustre/scratch126 | awk '/\/lustre\/scratch126/ {print $4}')
lustre_used=$(lfs quota -g team298 -h /lustre/scratch126 | awk '/\/lustre\/scratch126/ {print $2}')
#remove T from the values
used_num=$(echo "$lustre_used" | sed 's/[A-Za-z]//g')
size_num=$(echo "$lustre_size" | sed 's/[A-Za-z]//g')
#making used_value an integer
used_int=${used_num%.*}
size_int=${size_num%.*}
lustre_avail=$(echo $((size_int - used_int))'T')
lustre_percent=$(echo $((used_int*100/45))'%')
# nfs
#df -h /nfs/team298
nfs_size=$(df -h /nfs/team298 | sed -n '2p' | awk '{print $2}')
nfs_used=$(df -h /nfs/team298 | sed -n '2p' | awk '{print $3}')
nfs_avail=$(df -h /nfs/team298 | sed -n '2p' | awk '{print $4}')
nfs_percent=$(df -h /nfs/team298 | sed -n '2p' | awk '{print $5}')
# warehouse
#df -h /warehouse/team298_wh01
wh_size=$(df -h /warehouse/team298_wh01 | sed -n '2p' | awk '{print $2}')
wh_used=$(df -h /warehouse/team298_wh01 | sed -n '2p' | awk '{print $3}')
wh_avail=$(df -h /warehouse/team298_wh01 | sed -n '2p' | awk '{print $4}')
wh_percent=$(df -h /warehouse/team298_wh01 | sed -n '2p' | awk '{print $5}')
#/archive/team298 irods 
iquest --no-page -z archive "%s/%s,%s" "select COLL_NAME, DATA_NAME, DATA_SIZE where COLL_NAME like \
'/archive/team298%'" | tail -n +2 | sort | uniq > $TEAM_DATA_DIR/reports/storage/team298.irods.csv
archive_used=$(cut -f 2 -d , $OUTPUT_DIR/team298.irods.csv | paste -sd+ | bc | numfmt --to iec --format "%4.2f")
archive_size="20T"
#remove T's
archive_used_num=$(echo "$archive_used" | sed 's/[A-Za-z]//g')
archive_size_num=$(echo "$archive_size" | sed 's/[A-Za-z]//g')
#turn archive numbers into integers
archive_used_int=${archive_used_num%.*}
archive_size_int=${archive_size_num%.*}
#archive usage percentage 
archive_percent=$(echo $((archive_used_int*100/archive_size_int))'%')

# Array of data
data=("Lustre $lustre_size $lustre_used $lustre_avail $lustre_percent"
        "nfs $nfs_size $nfs_used $nfs_avail $nfs_percent"
        "warehouse $wh_size $wh_used $wh_avail $wh_percent"
        "/archive/team298 $archive_used $archive_size - $archive_percent")

# Define headers
printf "%-16s %-6s %-8s %-6s %-6s\n" "workspace" "size" "used" "avail" "use%"
printf "%-16s %-6s %-8s %-6s %-6s\n" "-------------" "-----" "------" "-----" "-----"

# Loop through data
for row in "${data[@]}"; do
    printf "%-16s %-6s %-8s %-6s %-6s\n" $row
done