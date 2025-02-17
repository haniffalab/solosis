#!/bin/bash

export LSB_DEFAULT_USERGROUP=team298

conda_env="/software/cellgen/team298/shared/envs/hl-conda/hl_scanpy_v0.3.0"
if [ $# -ne 2 ]; then
	echo "$0 samples_database sample_sheet.tsv"
	echo "This is a follow up of irods/pull-processed. If you have not run it, do so"
	echo "samples_database: Folder where you have all sample cellranger data. Ideally - /lustre/scratch126/cellgen/team298/sample_data/"
	echo "sample_name: Folder name of sample that contains the processed_sanger folder"
	exit 0
fi

samples_database=$1; shift
sample_tsv=$1; shift

#mkdir -p pap

HL_HIST_FOLDER=".pap"
mem=50000
target_dir=/lustre/scratch126/cellgen/team298/sample_data/ # This is obtained by module load hl
cwd=`pwd`
run_token=$RUN_TOKEN
ofile="rna_scanpy_$run_token.cmds"
rm -f $ofile
declare -i i=0
while read line
do
        i+=1
    if [ `echo $line | grep -c -i Sample` -ne 1 ]; then
        sanger_id=`echo $line | awk ' { print $1 } '`
        sample_id=`echo $line | awk ' { print $2 } '`
	sample_name="${sample_id}_${sanger_id}"
	#sample_folder="$samples_database/${sample_id}_${sanger_id}/processed_sanger/"
	outpt_folder="$samples_database/${sample_name}/rna_scanpy/"
	mkdir -p $outpt_folder
	echo "($i) [Info] $sample_name will be processed in $outpt_folder"
	cmd="papermill /software/cellgen/team298/shared/solosis/bin/nb/sc_base1.ipynb $outpt_folder/$sample_name.ipynb  -p samples_database '${samples_database}' -p sample_name $sample_name -k python3  --log-output"
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
cat > $bsub_id.bsub <<EOF
#!/bin/bash
#BSUB -J ${bsub_id}_[1-$total_jobs]%20
#BSUB -o $HL_HIST_FOLDER/lsf/${bsub_id}_%I.out
#BSUB -e $HL_HIST_FOLDER/lsf/${bsub_id}_%I.err
#BSUB -M $mem
#BSUB -R "select[mem>$mem] rusage[mem=$mem]"
conda activate $conda_env
COMMAND=\$(sed -n "\${LSB_JOBINDEX}p" $ofile) 
eval \$COMMAND
EOF

echo "[Info] batch job submitted. check using 'bjobs -w' command"
bsub < ${bsub_id}.bsub

