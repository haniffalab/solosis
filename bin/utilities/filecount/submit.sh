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

# Define headers
printf "%-12s %-10s %-10s \n" "workspace" "filecount" "file-limit"
printf "%-12s %-10s %-10s \n" "--------" "--------" "--------"


# Configure paths and job parameters
TEAM_LOGS_DIR="$HOME/logs"
CPU=16
MEM=64000
QUEUE="normal"
GROUP="team298"

# Ensure logs directory exists
mkdir -p "$TEAM_LOGS_DIR"

bsub -J "filecount" <<EOF
#!/bin/bash
#BSUB -o "$TEAM_LOGS_DIR/filecount_%J_%I.out"   # Standard output with array job index
#BSUB -e "$TEAM_LOGS_DIR/filecount_%J_%I.err"   # Standard error with array job index
#BSUB -n $CPU                                    # Number of CPU cores
#BSUB -M $MEM                                    # Memory limit in MB
#BSUB -R "span[hosts=1] select[mem>$MEM] rusage[mem=$MEM]" # Resource requirements
#BSUB -G $GROUP                                  # Group for accounting
#BSUB -q $QUEUE                                  # Queue name

# Loop through data
for row in "${data[@]}"; do
    printf "%-12s %-10s %-10s\n" $row
done
EOF

table=row
message="Dear User, \n 
\n
The filecount capacity for team298 is as follows: \n
$table 
\n
Thank you"

echo -e $message | mail -s "Lustre Quota Alert" nlg143@newcastle.ac.uk

echo "Submitted LSF job for filecount command."
