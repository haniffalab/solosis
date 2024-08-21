# hlpiper

A plug and play pipeline for the lab
This suite is made to work with farm22. The instructions below are to be performed in farm unless otherwise stated.

# Installation

1. Append your bashrc

```
echo "source /lustre/scratch126/cellgen/team298/soft/hl.bashrc" >> $HOME/.bashrc
source ~/.bashrc
```

2. Module load

```
module load hl-piper/v1.0.0
```

3. Main command help

```
hl..piperv100 --help
```
# scRNA seq analysis

SingleCell-Voyage retrieves FASTQ files from iRODS storage to Lustre storage on HPC, processes them with Cellranger and Cellbender, optionally aligns with STARsolo, and finally runs scAutoQC for streamlined sample data processing. 

Here sc-voyage has ben integrated into hl-piperv100 module.

1. Export environment variables

```
export VOY_CODE=/lustre/scratch126/cellgen/team298/pipelines/sc-voyage 
export VOY_TMP=/lustre/scratch126/cellgen/team298/tmp 
export VOY_DATA=/lustre/scratch126/cellgen/team298/sample_data 
export VOY_PIPELINES=/lustre/scratch126/cellgen/team298/pipelines
```

2. Populate samples.csv with sample IDs
```
nano /lustre/scratch126/cellgen/team298/pipelines/sc-voyage/samples.csv
```

3. Execute Cellranger
```
hl..piperv100 test cellranger
```

4. Execute Cellbender

The ```--total_droplets_included``` flag is required.

(For more information- ```hl..piperv100 test cellbender --help```)
```
hl..piperv100 test cellbender --total_droplets_included 30000
```


