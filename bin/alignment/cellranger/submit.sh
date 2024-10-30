#!/bin/bash
# LSF Array job script for Cell Ranger processing

# Load Cell Ranger module
module load cellgen/cellranger

# Set job parameters
GROUP="team298"
CPU=16
MEM=64000
Q="normal"
REF="/software/cellgen/cellgeni/refdata-gex-GRCh38-2020-A"
samples_list=$1      # Comma-separated list of sample IDs
include_bam_flag=$2  # BAM inclusion flag

# Check if sample list is empty
if [[ -z "$samples_list" ]]; then
  echo "Error: No samples provided." >&2
  exit 1
fi

# Determine BAM inclusion flag
bam_flag="--no-bam"
if [[ "$include_bam_flag" -eq "1" ]]; then
  bam_flag=""  # Remove flag if --includebam is specified
fi

# Convert the comma-separated list into an array
IFS=',' read -r -a samples_array <<< "$samples_list"

# Get the total number of samples
total_jobs=${#samples_array[@]}

# Submit the array job
bsub <<EOF
#!/bin/bash
#BSUB -J cellranger_array[1-$total_jobs]%20  # Limit to 20 jobs running concurrently
#BSUB -o $VOY_CODE/logs/%J_%I.bsub.log       # %I logs for job array index
#BSUB -e $VOY_CODE/logs/%J_%I.bsub.err
#BSUB -n $CPU
#BSUB -M $MEM
#BSUB -R "span[hosts=1] select[mem>${MEM}] rusage[mem=${MEM}]"
#BSUB -G $GROUP
#BSUB -q $Q

# Retrieve the sample ID corresponding to this job index
sample=\${samples_array[\$((LSB_JOBINDEX - 1))]}  # Adjust for zero-based indexing

# Run Cell Ranger for the sample
mkdir -p "$VOY_DATA/\$sample/cellranger"
if ! cellranger count --id="\$sample" --fastqs="$VOY_TMP/\$sample" --transcriptome="$REF" \
    --sample="\$sample" --localcores=$CPU --localmem=$((MEM / 1000)) --output-dir="$VOY_DATA/\$sample/cellranger" $bam_flag; then
    echo "Error during Cell Ranger execution for sample \$sample" >&2 >> "$VOY_CODE/logs/\$sample_cellranger_error.log"
    exit 1
fi
EOF
