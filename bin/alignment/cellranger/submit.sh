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
samples_file=$1
include_bam_flag=$2

# Check if sample file exists
if [[ ! -f "$samples_file" ]]; then
  echo "Error: Sample file '$samples_file' not found." >&2
  exit 1
fi

# Determine BAM inclusion flag
bam_flag="--no-bam"
if [[ "$include_bam_flag" -eq "1" ]]; then
  bam_flag=""  # Remove flag if --includebam is specified
fi

# Get the total number of samples (excluding header)
total_jobs=$(($(wc -l < "$samples_file") - 1))

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
sample=\$(sed -n "\$((LSB_JOBINDEX + 1))p" "$samples_file" | cut -d',' -f1)

# Run Cell Ranger for the sample
mkdir -p "$VOY_DATA/\$sample/cellranger"
if ! cellranger count --id="\$sample" --fastqs="$VOY_TMP/\$sample" --transcriptome="$REF" \
    --sample="\$sample" --localcores=$CPU --localmem=$((MEM / 1000)) --output-dir="$VOY_DATA/\$sample/cellranger" $bam_flag; then
    echo "Error during Cell Ranger execution for sample \$sample" >&2 >> "$VOY_CODE/logs/\$sample_cellranger_error.log"
    exit 1
fi
EOF
