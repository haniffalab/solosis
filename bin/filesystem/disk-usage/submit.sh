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

# Array of data
data=("Lustre $lustre_size $lustre_used $lustre_avail $lustre_percent"
        "nfs $nfs_size $nfs_used $nfs_avail $nfs_percent"
        "warehouse $wh_size $wh_used $wh_avail $wh_percent")

# Define headers
printf "%-12s %-6s %-8s %-6s %-6s\n" "workspace" "size" "used" "avail" "use%"
printf "%-12s %-6s %-8s %-6s %-6s\n" "---------" "-----" "------" "-----" "-----"

# Loop through data
for row in "${data[@]}"; do
    printf "%-12s %-6s %-8s %-6s %-6s\n" $row
done

####### including lustre quota script ######
#warning limit
warn_int=38

#Percentage equation
lustre_percentage=$(echo $((used_int*100/size_int))'%')

## text of the email 
message_lustre="Dear User, \n 
\n
The capacity for Lustre (team298) is at $lustre_percentage capacity: \n
Amount used: $lustre_used ($lustre_percentage) \n
Amount available: $lustre_size \n
\n
Please review contents of Lustre directory (/lustre/scratch126/cellgen/team298), and remove content that is no longer essential. \n
\n NOTE:Items that should not be permanently deleted can be stored on iRODS for secure storage. Find Haniffa Lab (Team298) storage space in /archive/team298 \n
\n Thank you."

#  this will change to if $used_value is more than 47.5T
if [ "$used_int" -gt "$warn_int" ]; then
    # Submit the email
    echo -e "$message_lustre" | mail -s "Lustre Quota Alert" nlg143@newcastle.ac.uk daniela.basurto-lozada@newcastle.ac.uk Dave.Horsfall@newcastle.ac.uk vm11@sanger.ac.uk
fi
