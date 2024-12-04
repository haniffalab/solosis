#!/bin/bash
# @lg28
# Thu  22 Aug 16:46:44 BST 2024

set -euo pipefail

## Exporting environment variables ##
export VOY_CODE=/lustre/scratch126/cellgen/team298/pipelines/sc-voyage
export VOY_TMP=/lustre/scratch126/cellgen/team298/tmp
export VOY_DATA=/lustre/scratch126/cellgen/team298/sample_data
export VOY_PIPELINES=/lustre/scratch126/cellgen/team298/pipelines

module load cellgen/star

GROUP="team298"
CPU=16
MEM=64000
Q="normal"

samples_file=$1

# Create an output file to hold the commands for each sample
commands_file=$(basename "$samples_file").commands
rm -f $commands_file #this isn't working?

# Read the sample file and prepare commands for each sample
tail -n +2 $samples_file | while IFS=, read -r sample; do
  echo "$VOY_CODE/starsolo/starsolo_10x_auto.sh $VOY_TMP/$sample $sample $VOY_DATA/$sample/starsolo" >> $commands_file
done

# Get the total number of jobs
total_jobs=$(wc -l < $commands_file)

# Create the LSF job array script
bsub_array_script="submit_starsolo_${RANDOM}.bsub"
cat > $bsub_array_script <<EOF
#!/bin/bash
#BSUB -J starsolo_array[1-$total_jobs]%20  # Limit to 20 jobs at once
#BSUB -o $VOY_CODE/logs/%J_%I.bsub.log        # %I is job index in array
#BSUB -e $VOY_CODE/logs/%J_%I.bsub.err
#BSUB -n $CPU
#BSUB -M $MEM
#BSUB -R "span[hosts=1] select[mem>${MEM}] rusage[mem=${MEM}]"
#BSUB -G $GROUP
#BSUB -q $Q

# Get the command for this job from the commands file
COMMAND=\$(sed -n "\${LSB_JOBINDEX}p" $commands_file)
eval \$COMMAND
EOF

# Submit the job array
bsub < $bsub_array_script
