#!/bin/bash
# @lg28
# Wed  11 Aug 13:22:34 BST 2024


set -euo pipefail

export VOY_CODE=/lustre/scratch126/cellgen/team298/pipelines/sc-voyage
export VOY_TMP=/lustre/scratch126/cellgen/team298/tmp
export VOY_DATA=/lustre/scratch126/cellgen/team298/sample_data
export VOY_PIPELINES=/lustre/scratch126/cellgen/team298/pipelines

module load cellgen/cellbender

GROUP="team298"
CPU=2
MEM=34000
Q="gpu-normal"
GMEM=6000  # GPU memory

samples_file=$1
DROPLETS=$2

# Create a file to store commands for each sample
commands_file=$(basename "$samples_file").commands
rm -f $commands_file ## unsure this works? 

# Loop through the CSV, generating commands for each sample
tail -n +2 $samples_file | while IFS=, read -r sample; do
  echo "mkdir -p $VOY_DATA/$sample/cellbender-results | cellbender remove-background --cuda --input $VOY_DATA/$sample/cellranger/outs/raw_feature_bc_matrix.h5 --output $VOY_DATA/$sample/cellbender-results/$sample-cb.h5 --total-droplets-included $DROPLETS" >> $commands_file
done

# Get the total number of jobs
total_jobs=$(wc -l < $commands_file)

# Create the LSF job array script
bsub_array_script="submit_cellbender_${RANDOM}.bsub"
cat > $bsub_array_script <<EOF
#!/bin/bash
#BSUB -J cellbender_array[1-$total_jobs]%20  # Limit to 20 jobs at once
#BSUB -o $VOY_CODE/logs/%J_%I.bsub.log         # %I is job index in array
#BSUB -e $VOY_CODE/logs/%J_%I.bsub.err
#BSUB -n $CPU
#BSUB -M $MEM
#BSUB -R "span[hosts=1] select[mem>${MEM}] rusage[mem=${MEM}]"
#BSUB -G $GROUP
#BSUB -q $Q
#BSUB -gpu "mode=shared:j_exclusive=no:gmem=${GMEM}:num=1:gmodel=NVIDIAA100_SXM4_80GB"

# Get the command for this job from the commands file
COMMAND=\$(sed -n "\${LSB_JOBINDEX}p" $commands_file)
eval \$COMMAND
EOF

# Submit the job array
bsub < $bsub_array_script

