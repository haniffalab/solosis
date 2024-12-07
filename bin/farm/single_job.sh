#!/bin/bash
# submit a farm job

# Exit immediately if a command exits with a non-zero status
set -e

#bsub -J $job_name -o ${job_name}_%J.log -e ${job_name}_%J.log -q $queue -n $ncores  -M$mem -R"select[mem>$mem] rusage[mem=$mem]" $@


LOG_FOLDER=".solosis"

# Check if the number of arguments is less than 4
#if [ $# -lt 4 ]; then
#  echo "Usage: $0 <job_name> <queue> <walltime> <ncores> <mem> <command>" >&2
#  echo "job_name: str, name of job" >&2
#  echo "queue: str, queue name" >&2
#  echo "walltime: str, wall time for the job" >&2
#  echo "ncores: int, number of cores" >&2
#  echo "mem: int, memory required" >&2
#  echo "command: str, command to execute" >&2
#  exit 1
#fi

# Assign positional parameters to variables and shift them
#job_name=$1; shift
#queue=$1; shift
#walltime=$1; shift
#ncores=$1; shift
#mem=$1; shift
#command=$@

#bash_submit(command, jobname="testing", queue=queue, time=time, cores=cores, mem=mem, command = "echo 'Hello, World!'")

if [ ! -d $LOG_FOLDER/lsf ]; then
  mkdir -p $LOG_FOLDER
fi

bsub_file=$job_name.lsf


cat > $bsub_file <<eof
#!/bin/bash
set -euo pipefail
#bsub -j $job_name
#bsub -q $queue
#bsub -o $LOG_FOLDER/lsf/$job_name.log
#bsub -n $ncores 
#bsub -m $mem
#bsub -r "select[mem>$mem] rusage[mem=$mem]"
#bsub -w $walltime
eval \$command
eof

bsub < $bsub_file
