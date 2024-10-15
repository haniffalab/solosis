#!/bin/bash
# @lg28
# Tue  27 Aug 15:11:02 BST 2024

# LSF group is set and visible for nextflow job submissions
export LSB_DEFAULT_USERGROUP=team298

##lg28 added these to original run.sh from cellgen
export VOY_TMP=/lustre/scratch126/cellgen/team298/tmp
#export NXF_FILE_ROOT=$VOY_TMP
export NXF_WORK=/lustre/scratch126/cellgen/team298/pipelines/nf-irods-to-fastq/work
module load cellgen/irods
module load cellgen/nextflow
module load cellgen/singularity

# add Singularity to the the path
export PATH="/software/singularity/v3.10.0/bin:$PATH"

#input file, CSV with irods metadata
META=$1

cmd="NXF_FILE_ROOT=$VOY_TMP nextflow run /lustre/scratch126/cellgen/team298/pipelines/nf-irods-to-fastq/main.nf \
    --meta \"${META}\" \
    -resume"
#META="/lustre/scratch126/cellgen/team298/pipelines/nf-irods-to-fastq/examples/samples.csv"

usage() {
	echo "Usage: $0 samples.csv"
	echo "sample.csv example is in /lustre/scratch126/cellgen/team298/pipelines/nf-irods-to-fastq/examples/samples.csv"
}

if [ $# -lt 1 ]; then
	usage
	exit 0
fi

# NF_PUBLISH_DIR=/lustre/scratch126/cellgen/team298/tmp/
# samplefile="irods2fastq.$RUN_TOKEN.txt"

# echo "sample" > irods2fastq.$RUN_TOKEN.txt
# awk ' { print $1 } ' $META >> $samplefile
# cmd="nextflow run $HL_NF_BASE/nf-irods-to-fastq/main.nf \
#     --meta \"${samplefile}\" \
#     -resume \
#     --publish_dir $NF_PUBLISH_DIR
#     "
# echo $cmd
exec $cmd
