#!/bin/bash
# submit.sh - Environment setup for filecount of workspaces on Farm22

# Usage:
#   ./submit.sh 
#
# Parameters:
#   <change-this> - NOTHING ESSENTIAL

# lustre
#lfs quota -g team298 -h /lustre/scratch126
file_count=$(lfs quota -g team298 -h /lustre/scratch126 | sed -n '4p' | awk '{print $5}')
file_limit=$(lfs quota -g team298 -h /lustre/scratch126 | sed -n '4p' | awk '{print $7}')

# nfs
# df -h /nfs/team298
#nfs_count=$(find /nfs/team298 -type f | wc -l)

#warehouse
#df -h /warehouse/team298_wh01
wh_count=$(find /warehouse/team298_wh01 -type f | wc -l)


# Array of data
data=("Lustre $file_count $file_limit "
        "nfs nfs_count nfs_lim "
        "warehouse $wh_count wh_lim ")

GROUP="team298"
CPU=2
MEM=3000
Q="normal"
TEAM_LOGS_DIR="$HOME/logs"

bsub -J "filecount" <<EOF
#!/bin/bash
#BSUB -n $CPU \
#BSUB -M $MEM \
#BSUB -R"span[hosts=1] select[mem>${MEM}] rusage[mem=${MEM}]" \
#BSUB -G $GROUP \
#BSUB -q $Q \
#BSUB -o "$TEAM_LOGS_DIR/filecount.out" \
#BSUB -e "$TEAM_LOGS_DIR/filecount.err" \

# Define headers
printf "%-12s %-10s %-10s \n" "workspace" "filecount" "file-limit"
printf "%-12s %-10s %-10s \n" "--------" "--------" "--------"

# Loop through data
process_array() {
    for row in "${data[@]}"; do
        printf "%-12s %-10s %-10s\n" $row
    done
}

EOF


#echo "Submitted LSF job for filecount command."
