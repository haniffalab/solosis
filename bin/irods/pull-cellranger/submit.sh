#!/bin/bash
# @vm11
# Thu  6 Jun 13:15:00 BST 2024

#file="2024_04_16_samples_viki.tsv"

if [ $# -ne 3 ]; then
    echo "$0 samples.txt retain_bam[0/1] overwrite[0/1]"
    echo "Input example is in /software/cellgen/team298/shared/hlpiper_v1.0.0/examples/irods_download.txt"
    echo "Input file should have 3 mandatory columns"
    echo "1st column: sanger_id"
    echo "2nd column: sample_name"
    echo "LAST column: irods path"
    echo "You can have any column in between"
    exit 0
fi

HL_HIST_FOLDER=".pap/"

#### INPUT #### 
file=$1; shift
retain_bam=$1; shift
overwrite=$1

ofile=$(basename $file).irods
#retain_bam=0
rm -f $ofile
#target_dir=$HL_IRODS_DOWNLOAD # This is obtained by module load hl
target_dir=/lustre/scratch126/cellgen/team298/sample_data/
cwd=`pwd`
rn=$RANDOM
rn=$RUN_TOKEN
echo $rn
####


#### FARM options ####
queue="normal"
walltime="05:00:00"
mem=4000
#bsub_command="bsub -J irods_dl -oo irods_dl_${rn}.log -eo irods_dl_${rn}.log -q $queue -n 1  -M$mem -R\"select[mem>$mem] rusage[mem=$mem]\" "
irods_command="iget -KVf --progress -r "
####
declare -i i=0

while read line
do
	i+=1
    if [ `echo $line | grep -c -i Sample` -ne 1 ]; then
        sanger_id=`echo $line | awk ' { print $1 } '`
        sample_id=`echo $line | awk ' { print $2 } '`
        irods_path=`echo $line | awk ' { print $NF } '`
        folder_name="$target_dir/${sample_id}_${sanger_id}"
        target_name="$folder_name/processed_sanger/"
	mkdir -p $folder_name
	if [ $overwrite -eq 1 ]; then
		rm -rf $target_name
	fi
	if [ -d $target_name ]; then
		echo "[Warn] Target folder already exists. Not downloading. Try overwrite option if you want to download. Irods::$irods_path --> Folder::$target_name "
		echo "[Warn] Just linking them"
		ln -s $folder_name $cwd/
	else
		echo "($i)[Info] Irods::$irods_path --> Folder::$target_name"
		if [ $retain_bam == 1 ]; then
			echo "$irods_command $irods_path $target_name ; chmod -R 774 $folder_name ;  ln -s $folder_name $cwd/" >>  $ofile
		else
			echo "$irods_command $irods_path $target_name ; chmod -R 774 $folder_name ; rm -rf $target_name/gex_possorted_bam.bam ; find $target_name -name 'possorted_genome_bam.bam' -exec rm -rf {} \; ; ln -s $folder_name $cwd/" >>  $ofile
		fi

	fi
    fi
done < $file

if [ ! -f $ofile ]; then
	echo "Looks like nothing needs to be done"
	echo "Exiting cleanly..."
	exit 0
fi

total_jobs=$(cat $ofile | wc -l)

cat > irods_dl_${rn}.bsub <<EOF
#!/bin/bash
#BSUB -J irods_dl_${rn}_[1-$total_jobs]%20
#BSUB -o $HL_HIST_FOLDER/lsf/irods_dl_${rn}_%I.out
#BSUB -e $HL_HIST_FOLDER/lsf/irods_dl_${rn}_%I.err
#BSUB -M $mem
#BSUB -R "select[mem>$mem] rusage[mem=$mem]"
COMMAND=\$(sed -n "\${LSB_JOBINDEX}p" $ofile) 
eval \$COMMAND
EOF
echo "[Info] batch job submitted. check using 'bjobs -w' command"
bsub < irods_dl_${rn}.bsub
