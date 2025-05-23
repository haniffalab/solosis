#!/bin/bash

export LSB_DEFAULT_USERGROUP=team298

conda_env="/software/cellgen/team298/shared/envs/hl-conda/hl_scanpy_v0.3.0"
if [ $# -ne 2 ]; then
	echo "$0 sample_sheet.tsv merged_filename"
	echo "sample_table: sampletable.tsv"
	echo "merged_filename: name of output file name"
	exit 0
fi


sample_table="sample_test.txt"
datatable_type="tsv"
n_top_genes=2000
merged_filename="outpt.h5ad"
mem=50000

sample_table=$1; shift
merged_filename=$1; shift

#mkdir -p pap

HL_HIST_FOLDER=".pap"
target_dir=/lustre/scratch126/cellgen/team298/sample_data/ # This is obtained by module load hl
cwd=`pwd`
run_token=$RUN_TOKEN
outpt_prefix=`echo $merged_filename | sed -e 's/.h5ad//g'`
echo "Your run token is: $run_token"
cmd="papermill /software/cellgen/team298/shared/solosis/bin/nb/rna__merge.ipynb merge_$outpt_prefix.ipynb -p sample_table $sample_table -p merged_filename $merged_filename -k python3;"


bsub_id="rna_merge_${run_token}"
echo "Generating a bsub script $bsub_id.bsub"
cat > $bsub_id.bsub <<EOF
#!/bin/bash
#BSUB -J ${bsub_id}
#BSUB -o $HL_HIST_FOLDER/lsf/${bsub_id}_%I.out
#BSUB -e $HL_HIST_FOLDER/lsf/${bsub_id}_%I.err
#BSUB -M $mem
#BSUB -R "select[mem>$mem] rusage[mem=$mem]"
conda activate $conda_env
eval $cmd
EOF
jid=`bsub < ${bsub_id}.bsub`
echo $jid

