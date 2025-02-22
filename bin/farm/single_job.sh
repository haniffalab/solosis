#!/bin/bash
# submit a farm job

# Exit immediately if a command exits with a non-zero status
set -e

#bsub -J $job_name -o ${job_name}_%J.log -e ${job_name}_%J.log -q $queue -n $ncores  -M$mem -R"select[mem>$mem] rusage[mem=$mem]" $@


LOG_FOLDER=".solosis"

if [ ! -d $LOG_FOLDER/lsf ]; then
  mkdir -p $LOG_FOLDER/lsf
fi

# Creates an lsf folder in the current directory.
# TODO: Append the solosis RUNID to this. 
bsub_file=$LOG_FOLDER/lsf/${job_name}.lsf

email="$USER@sanger.ac.uk"
cat > $bsub_file <<eof
#!/bin/bash
#BSUB -J $job_name
#BSUB -q $queue
#BSUB -n $cores 
#BSUB -M $mem
#BSUB -R "select[mem>$mem] rusage[mem=$mem]"
#BSUB -W $time
#BSUB -o $LOG_FOLDER/lsf/${job_name}.log
#BSUB -Ep /software/cellgen/cellgeni/etc/notify-slack.sh # CellGen Slack notification support

set -euo pipefail
$command_to_exec
status=\$?
# Email job exit status
if [ \$status -eq 0 ]; then
  job_status="\$command_to_exec \n command was successful: Exit status: \$status"
 
else
  job_status="\$command_to_exec \n command failed: Exit status: \$status"
fi
echo \$job_status | mail -s "Job status: $job_name" $email
eof

bsub < $bsub_file