#!/bin/bash

export LSB_DEFAULT_USERGROUP=team298
conda_env="/software/cellgen/team298/shared/envs/hlb-conda/rna"
if [ $# -ne 2 ]; then
	echo "$0 samples_database sample_sheet.tsv"
	echo "This is a follow up of irods/pull-processed. If you have not run it, do so"
	echo "samples_database: Folder where you have all sample cellranger data. Ideally - /lustre/scratch124/cellgen/haniffa/data/samples"
	echo "sample_name: Folder name of sample that contains the processed_sanger folder"
	exit 0
fi

samples_database=$1; shift
sample_tsv=$1; shift

#mkdir -p pap

mem=50000
target_dir=`pwd` # This is obtained by module load hl
cwd=`pwd`
run_token=$RUN_TOKEN
ofile="rna_scanpy_$run_token.cmds"
rm -f $ofile
HL_HIST_FOLDER="$cwd/.solosis"

declare -i i=0
while read line
do
        i+=1
    if [ `echo $line | grep -c -i Sample` -ne 1 ]; then
        sample_id=`echo $line | awk ' { print $1 } '`
        sample_name=`echo $line | awk ' { print $2 } '`
        cellranger_folder=`echo $line | awk ' { print $NF } '`
        cellranger_folder=`basename $cellranger_folder`

	#sample_name="${sample_id}_${sanger_id}"
	#sample_folder="$samples_database/${sample_id}_${sanger_id}/processed_sanger/"
	#outpt_folder="$samples_database/${sample_name}/rna_scanpy/"
    outpt_folder="$cwd/rna_scanpy/"
	mkdir -p $outpt_folder
	echo "($i) [Info] $sample_name will be processed in $outpt_folder"
    echo "$solosis_dir"
	#="papermill $solosis_dir/../../../notebooks/sc_base1.ipynb $outpt_folder/$sample_name.ipynb  -p samples_database '${samples_database}' -p sample_name $sample_name -k python3  --log-output"
    cmd="conda activate $conda_env &&  papermill $solosis_dir/../../../notebooks/sc_base1.ipynb $outpt_folder/${sample_name}_${sample_id}.ipynb  -p samples_database '${samples_database}' -p sample_name $sample_name -p sample_id $sample_id -p cellranger_folder cellranger/$cellranger_folder --log-output"
	echo $cmd >> $ofile
    fi
done < $sample_tsv

if [ ! -f $ofile ]; then
        echo "Looks like nothing needs to be done"
        echo "Exiting cleanly..."
        exit 0
fi

total_jobs=$(cat $ofile | wc -l)
bsub_id="rna_scanpy_${run_token}"
lsf_folder="$HL_HIST_FOLDER/lsf"
mkdir -p $lsf_folder
cat > $bsub_id.bsub <<EOF
#!/bin/bash
#BSUB -J ${bsub_id}_[1-$total_jobs]%20
#BSUB -o $lsf_folder/${bsub_id}_%I.out
#BSUB -e $lsf_folder/${bsub_id}_%I.err
#BSUB -M $mem
#BSUB -R "select[mem>$mem] rusage[mem=$mem]"
conda activate $conda_env
COMMAND=\$(sed -n "\${LSB_JOBINDEX}p" $ofile) 
eval \$COMMAND
EOF

echo "[Info] batch job submitted. check using 'bjobs -w' command"
bsub < ${bsub_id}.bsub

