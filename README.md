# Haniffa-utils

A plug and play pipeline for the lab
This suite is made to work with farm22. The instructions below are to be performed in farm unless otherwise stated.

# Installation

1. Append your bashrc

```
echo "source /software/cellgen/team298/shared/hl.bashrc" >> $HOME/.bashrc
source ~/.bashrc

#move to home dir
cd
```

2. Module load

```
module load haniffa-utils
```

3. Main command help

```
hl..solosis1 --help
```
# scRNA seq analysis

SingleCell-Voyage retrieves FASTQ files from iRODS storage to Lustre storage on HPC, processes them with Cellranger and Cellbender, optionally aligns with STARsolo, and finally runs scAutoQC for streamlined sample data processing. 

Here sc-voyage has been integrated into hl-solosis1 module.

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

3. Run the NF-irods-to-lustre pipeline to pull fastqs

```
hl..solosis1 irods pull-fastqs --sampefile path/to/file.csv
```

4. Execute Cellranger
```
hl..solosis1 alignment cellranger
```

5. [OPTIONAL] run STARsolo
```
hl..solosis1 alignment starsolo
```

7. Execute Cellbender

The ```--total_droplets_included``` flag is required.

(For more information- ```hl..solosis1 scRNA_analysis cellbender --help```)
```
hl..solosis1 rna cellbender --total_droplets_included 30000
```

# Development

Install dev dependencies and install pre-commit hooks

```
python -m venv .venv
source .venv/bin/activate
python -m pip install -r envs/dev/requirements.txt
pre-commit install
```

