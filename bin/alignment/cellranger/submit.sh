#!/bin/bash
# LSF Array job script for Cell Ranger processing

# Load Cell Ranger module
if ! module load cellgen/cellranger/$2; then
    echo "Error: Failed to load Cell Ranger version $2." >&2
    exit 1
fi

# Set temporary VOY environment variables
export TEAM_SAMPLE_DATA_DIR="/lustre/scratch126/cellgen/team298/data"
export TEAM_TMP_DATA_DIR="/lustre/scratch126/cellgen/team298/tmp"

# Set job parameters
GROUP="team298"
CPU=16
MEM=64000
Q="normal"
REF="/software/cellgen/cellgeni/refdata-gex-GRCh38-2020-A"
samples_list=$1      # Comma-separated list of sample IDs
include_bam_flag=$3  # BAM inclusion flag

# Check if sample list is empty
if [[ -z "$samples_list" ]]; then
  echo "Error: No samples provided." >&2
  exit 1
fi

# Determine BAM inclusion flag
bam_flag="--no-bam"
if [[ "$include_bam_flag" -eq "1" ]]; then
  bam_flag="" # Remove flag if --includebam is specified
fi

# Convert the comma-separated list into an array
IFS=',' read -r -a samples_array <<< "$samples_list"

# Get the total number of samples
total_jobs=${#samples_array[@]}

# Submit the array job
bsub <<EOF
#!/bin/bash
#BSUB -J cellranger_array[1-$total_jobs]%20  # Limit to 20 jobs running concurrently
#BSUB -o $HOME/logs/%J_%I.bsub.log       # %I logs for job array index
#BSUB -e $HOME/logs/%J_%I.bsub.err
#BSUB -n $CPU
#BSUB -M $MEM
#BSUB -R "span[hosts=1] select[mem>${MEM}] rusage[mem=${MEM}]"
#BSUB -G $GROUP
#BSUB -q $Q

# Retrieve the sample ID corresponding to this job index
sample=\${samples_array[\$((LSB_JOBINDEX - 1))]}  # Adjust for zero-based indexing

# Run Cell Ranger for the sample
mkdir -p "$TEAM_SAMPLE_DATA_DIR/\$sample/cellranger"
if ! cellranger count --id="\$sample" --fastqs="$TEAM_TMP_DATA_DIR/\$sample" --transcriptome="$REF" \
    --sample="\$sample" --localcores=$CPU --localmem=$((MEM / 1000)) --output-dir="$TEAM_SAMPLE_DATA_DIR/\$sample/cellranger" $bam_flag; then
    echo "Error during Cell Ranger execution for sample \$sample" >&2
    exit 1
fi
EOF
