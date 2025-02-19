#!/software/cellgen/team298/shared/envs/solosis-env/bin/python

import glob
import logging
import os
import sys
from pathlib import Path

import anndata as an
import click
import numpy as np
import pandas as pd
import scanpy as sc
import seaborn as sns
from matplotlib import pyplot as plt
from rich.logging import RichHandler
from scipy.stats import median_abs_deviation

logging.basicConfig(level=logging.INFO, handlers=[RichHandler()])
sc.settings.verbosity = 0
sc.settings.set_figure_params(
    dpi=80,
    facecolor="white",
    frameon=False,
)


def is_outlier(adata, metric: str, nmads: int):
    M = adata.obs[metric]
    outlier = (M < np.median(M) - nmads * median_abs_deviation(M)) | (
        np.median(M) + nmads * median_abs_deviation(M) < M
    )
    return outlier


def print_file(filename):
    with open(filename, "r") as f:
        print(f.readlines())


# set env variable
os.environ["REPO_DIR"] = "/nfs/users/nfs_l/lg28/repos/solosis"
# define team data directory
team_data_dir = "/lustre/scratch126/cellgen/team298/data/samples"
###### ADD BACK IN AFFTER TESTING #####
# team_data_dir = os.getenv("TEAM_SAMPLE_DATA_DIR")


@click.command()
@click.argument("samplefile_path", type=click.Path(exists=True))
def main(samplefile_path):
    """Merge single-cell datasets listed in SAMPLEFILE_PATH"""

    # user input values (add to config file instead?)
    # sample_table = "sample_test.txt" #removing because not needed
    datatable_type = "tsv"
    n_top_genes = 2000
    merged_filename = "merged_obj.h5ad"
    gex_only = True
    pct_mit_cutoff = 20
    min_cells_cutoff = 50
    min_genes_cutoff = 100
    sim_doublet_ratio = 5
    target_sum = 10000
    n_top_genes = 2000
    n_comps = 50  # pca
    n_pcs = 50  # kNN
    resolution = 1  # leiden
    min_dist = 0.5  # UMAP
    spread = 1  # UMAP

    # will use samplefile flag from click cli to read in list.. but for now going to read in samplefile from here
    samplefile = pd.read_csv(samplefile_path, index_col=None)

    # define out dir
    out_directory = Path("/lustre/scratch126/cellgen/team298/data/merged_samples")
    print(f"Output directory: {out_directory}")

    ### changing working directory, this can maybe be put in bash script later on..
    print("Before:", os.getcwd())  # Get current working directory
    os.chdir(out_directory)  # Change directory
    print("After:", os.getcwd())

    x = []
    for i in samplefile["sample_id"]:
        h5ad = Path(team_data_dir, i, "rna_scanpy", i + ".h5ad")
        print("Reading file: ", h5ad)
        try:
            x.append(sc.read_h5ad(h5ad))
        except:
            print("File not found")

    adata = an.concat(x, label="batch")

    ## why are we annotating these again?
    # mitochondrial genes
    adata.var["mt"] = adata.var_names.str.startswith("MT-")
    # ribosomal genes
    adata.var["ribo"] = adata.var_names.str.startswith(("RPS", "RPL"))
    # hemoglobin genes.
    adata.var["hb"] = adata.var_names.str.contains(("^HB[^(P)]"))

    ### why are we doing qc again?
    sc.pp.calculate_qc_metrics(adata, inplace=True)
    sc.pp.calculate_qc_metrics(
        adata, qc_vars=["mt", "ribo", "hb"], inplace=True, percent_top=[20], log1p=True
    )

    ## some plots.. where shall we save them?
    sc.pl.violin(adata, "pct_counts_mt", groupby="batch", save="_mt_counts.png")
    sc.pl.scatter(
        adata, "total_counts", "n_genes_by_counts", color="batch", save="_counts.png"
    )

    sc.pp.highly_variable_genes(adata, n_top_genes=n_top_genes, batch_key="batch")

    ## dimensional reduction

    # PCA
    ## repeating to understand how the samples are looking whe combined/integrated?
    sc.pp.pca(adata, use_highly_variable=True, n_comps=n_comps)

    ax = sns.scatterplot(
        data=adata.var, x="means", y="dispersions", hue="highly_variable", s=5
    )
    ax.set_xlim(None, 1.5)
    ax.set_ylim(None, 3)
    plt.show()
    plt.savefig(out_directory / "figures" / "pca_hvg")
    # save?

    reqCols = ["n_genes_by_counts", "total_counts", "pct_counts_mt"]
    sc.pl.pca_scatter(adata, color=reqCols, save="_reqCols.png")
    # save?

    ## kNN, clustering and UMAP

    ## repeating to understand how the samples are looking when combined/integrated?
    sc.pp.neighbors(adata, n_pcs=n_pcs)

    sc.tl.leiden(adata, resolution=resolution)

    # UMAP
    sc.tl.umap(adata, min_dist=min_dist, spread=spread)
    reqCols.extend(["leiden"])
    reqCols

    sc.pl.umap(adata, color=reqCols, ncols=3, save="_reqCols.png")
    # save?

    ##saving merged h5ad object
    merged_filename = (
        merged_filename if "h5ad" in merged_filename else merged_filename + ".h5ad"
    )
    adata.write_h5ad(os.path.join(out_directory, merged_filename))


if __name__ == "__main__":
    main()
