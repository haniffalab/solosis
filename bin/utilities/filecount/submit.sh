#!/bin/bash
# integrated_submit.sh - Generate file count report and submit as LSF job

TEAM_LOGS_DIR="$HOME/logs"
CPU=2
MEM=3000
QUEUE="normal"
GROUP="team298"

# Check if the script is running inside an LSF job
if [ -z "$LSB_JOBID" ]; then
    # If not running in LSF, submit itself as a job
    bsub <<EOF
#!/bin/bash
#BSUB -J filecount_job      # Job name
#BSUB -o "$TEAM_LOGS_DIR/filecount.out"      # Standard output file
#BSUB -e "$TEAM_LOGS_DIR/filecount.err"      # Standard error file
#BSUB -n $CPU                  # Number of cores
#BSUB -M $MEM               # Memory limit in MB
#BSUB -R "span[hosts=1] select[mem>$MEM] rusage[mem=$MEM]" # Resource requirements
#BSUB -G $GROUP                                  # Group for accounting
#BSUB -q $QUEUE                                  # Queue name
#BSUB -u nlg143@newcastle.ac.uk  # Email for job updates
#BSUB -B                    # Notify at the start of the job
#BSUB -N                    # Notify at the end of the job

bash $0 "$@"
EOF
    exit 0
fi

# If running in LSF, generate the report
# Lustre
file_count=$(lfs quota -g team298 -h /lustre/scratch126 2>/dev/null | sed -n '4p' | awk '{print $5}')
file_limit=$(lfs quota -g team298 -h /lustre/scratch126 2>/dev/null | sed -n '4p' | awk '{print $7}')

# NFS
nfs_count=$(find /nfs/team298 -type f | wc -l)
nfs_limit="N/A" # Update with real limits if available

# Warehouse
wh_count=$(find /warehouse/team298_wh01 -type f | wc -l)
wh_limit="N/A" # Update with real limits if available

# Define output file
output_file="filecount_report.txt"

# Write the table to the file
{
    printf "%-12s %-10s %-10s\n" "Workspace" "Filecount" "File-limit"
    printf "%-12s %-10s %-10s\n" "---------" "---------" "----------"
    printf "%-12s %-10s %-10s\n" "Lustre" "$file_count" "$file_limit"
    printf "%-12s %-10s %-10s\n" "NFS" "$nfs_count" "$nfs_limit"
    printf "%-12s %-10s %-10s\n" "Warehouse" "$wh_count" "$wh_limit"
} > "$output_file"

# email message 
message = "Dear user,
\n
the file count for workspaces available to Team298 on Farm22 are as follows: \n
[ INSERT TABLE HERE ]
\n
\n
Thank you."



# Email the report
#mailx -s "Workspace Filecount Report" your_email@example.com 
mail -s "Workspace Filecount Report" nlg143@newcastle.ac.uk < "$output_file"
#echo -e $message | mail -s "Workspace Filecount Report" nlg143@newcastle.ac.uk