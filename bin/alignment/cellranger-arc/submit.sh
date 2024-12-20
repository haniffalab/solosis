#!/bin/bash
# @lg28
# Mon  14  Oct 13:02:23 BST 2024

### this script is okay and contains arrays for lsf submission

## Exporting environment variables ##
export VOY_CODE=/lustre/scratch126/cellgen/team298/pipelines/sc-voyage
export VOY_TMP=/lustre/scratch126/cellgen/team298/tmp
export VOY_DATA=/lustre/scratch126/cellgen/team298/sample_data
export VOY_PIPELINES=/lustre/scratch126/cellgen/team298/pipelines

module load cellgen/cellranger-arc

set -euo pipefail

GROUP="team298"
CPU=16
MEM=64000
Q="normal"

REF=/software/cellgen/cellgeni/refdata-cellranger-arc-GRCh38-2020-A-2.0.0
samples_file=$1
LIB=$2
#include_bam_flag=$3

# Create an output file to hold the commands for each sample
commands_file=$(basename "$samples_file").commands
rm -f $commands_file

# Read the sample file and prepare commands for each sample
tail -n +2 $samples_file | while IFS=, read -r sample; do
  # Include or exclude the --no-bam flag based on include_bam_flag
#  bam_flag="--no-bam"
#  if [ "$include_bam_flag" -eq "1" ]; then
#    bam_flag=""  # No --no-bam flag if --includebam is passed
#  fi

  echo "mkdir -p $VOY_DATA/$sample/cellrangerARC | cellranger-arc count --id=$sample --libraries=$LIB --reference=$REF --localcores=16 --localmem=60" >> $commands_file # add $bam_flag back in 
done

# Get the total number of jobs
total_jobs=$(wc -l < $commands_file)

# Create the LSF job array script
bsub_array_script="submit_cellrangerARC_${RANDOM}.bsub"
cat > $bsub_array_script <<EOF
#!/bin/bash
#BSUB -J cellrangerARC_array[1-$total_jobs]%20  # Limit to 20 jobs at once
#BSUB -o $VOY_CODE/logs/%J_%I.bsub.log         # %I is job index in array
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
