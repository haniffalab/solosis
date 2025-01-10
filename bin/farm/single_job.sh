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
SOLOSIS_RUNID="solosis_runid"
bsub_prefix="${job_name}-${SOLOSIS_RUNID}"
bsub_file=$LOG_FOLDER/lsf/$bsub_prefix.lsf

email="$USER@sanger.ac.uk"
cat > $bsub_file <<eof
#!/bin/bash
#BSUB -J $job_name
#BSUB -q $queue
#BSUB -n $cores 
#BSUB -M $mem
#BSUB -R "select[mem>$mem] rusage[mem=$mem]"
#BSUB -W $time
#BSUB -o $LOG_FOLDER/lsf/$bsub_prefix.log
set -euo pipefail
$command_to_exec
status=\$?
if [ \$status -eq 0 ]; then
  echo "$command command was successful: Exit status: \$status" | mail -s "Job status: $job_name" $email
else
  echo "$cmd command failed: Exit status: \$status" | mail -s "Job status: $job_name" $email
fi
eof

bsub < $bsub_file