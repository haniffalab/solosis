import glob
import os
import sys
from pathlib import Path

import numpy as np
import scanpy as sc
import seaborn as sns
from matplotlib import pyplot as plt
from scipy.stats import median_abs_deviation

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


def run_qc(samples):
    print(f"running")
    return True

    # set env variable
    os.environ["REPO_DIR"] = "/nfs/users/nfs_l/lg28/repos/solosis"

    # check env variable
    repo_dir = os.environ.get("REPO_DIR")
    print(repo_dir)

    ########## syntax err?
    # call config file
    #!cat scanpy_rna_config.py
    ###########

    # User input values
    # setting user input values
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

    # loading raw data
    # defining paths
    team_data_dir = "/lustre/scratch126/cellgen/team298/data/samples"
    sample_name = "HCA_SkO14542035"
    # sample_list = []

    # read input file
    x = list(
        Path(
            os.path.join(
                team_data_dir, sample_name, "cellranger/7.2.0/HCA_SkO14542035/outs"
            )
        ).rglob("filtered_feature_bc_matrix.h5")
    )
    print(f"Files found: {x}")
    readfilename = x[0]
    readfilename
    # check adata object is read in properly
    adata = sc.read_10x_h5(readfilename, gex_only=gex_only)
    adata.var_names_make_unique()
    adata

    # add index column
    adata.obs.index = list(
        map(lambda x: str.split(x, "-")[0] + "_" + sample_name, list(adata.obs.index))
    )
    adata.obs["sample_name"] = sample_name

    # raw adata cell counts
    cells_raw = adata.n_obs
    cells_raw

    # Combine metadata to adata object
    # Read in metadata
    # metadata_csv = pd.read_csv("/path/to/file/metadata.csv", low_memory=False)
    # Merging based on the common columns 'Sanger_ID' and 'sanger_id'
    # raw_metadata = pd.merge(adata.obs, metadata_csv, left_on='sanger_id', right_on='Sanger_ID', how='left')

    # raw_metadata
    # define index column
    # adata.obs['index1'] = adata.obs.index + "-" + adata.obs['sanger_id']
    # adata.obs.index
    # raw_metadata.set_index('index1', inplace=True)
    # raw_metadata

    ########### decide about whether to save raw object (pre QC and filtering) #############
    # make copy of raw object
    # raw_adata_copy= adata

    # if we want raw object to process manually?
    out_directory = Path(os.path.join(team_data_dir, sample_name, "rna_scanpy"))
    # adata.write(out_directory + 'raw_merged.h5ad')

    ## Remove bad quality cells and low value genes
    # * mitochondrial genes
    # * haemoglobin genes
    # * ribosomal genes
    # * Genes in less cells
    # * Remove cells with less genes

    ## annotating genes with label to define gene types
    # mitochondrial genes
    adata.var["mt"] = adata.var_names.str.startswith("MT-")
    # ribosomal genes
    adata.var["rb"] = adata.var_names.str.startswith(("RPS", "RPL"))
    # hemoglobin genes.
    adata.var["hb"] = adata.var_names.str.contains(("^HB[^(P)]"))

    # calculating QC metrics
    ##calculate the respective QC metrics

    sc.pp.calculate_qc_metrics(adata, inplace=True)
    sc.pp.calculate_qc_metrics(
        adata, qc_vars=["mt", "rb", "hb"], inplace=True, percent_top=[20], log1p=True
    )

    ## setting cutoffs
    min_cells = np.round(adata.shape[0] * 0.005)
    if min_cells > min_cells_cutoff:
        min_cells = min_cells_cutoff
    min_counts = 1

    ##is this correct?
    min_genes = np.round(adata.shape[0] * 0.005)
    if min_cells > min_cells_cutoff:
        min_cells = min_cells_cutoff
    min_counts = 1

    p1 = sc.pl.violin(
        adata,
        ["n_genes_by_counts", "total_counts", "pct_counts_mt", "pct_counts_rb"],
        jitter=0.4,
        multi_panel=True,
    )

    ### save p1

    p3 = sns.displot(adata.obs["total_counts"], bins=100, kde=False)
    ### save p3

    p4 = sc.pl.violin(adata, "pct_counts_mt")
    ### save p4

    p5 = sc.pl.scatter(
        adata, "total_counts", "n_genes_by_counts", color="pct_counts_mt"
    )
    ### save p5

    ### defining outliers
    # Calculating outlier based on median absolute deviations (MAD).
    # median_abs_deviation function defined on line 19

    adata.obs["outlier"] = (
        is_outlier(adata, "log1p_total_counts", 5)
        | is_outlier(adata, "log1p_n_genes_by_counts", 5)
        | is_outlier(adata, "pct_counts_in_top_20_genes", 5)
    )
    outlier_counts = adata.obs.outlier.value_counts()
    outlier_counts

    # printing value for counts table
    outlier_true_count = outlier_counts.get(
        True, 0
    )  # Get count of True, default to 0 if not present
    print(outlier_true_count)

    # defining mt_outliers
    adata.obs["mt_outlier"] = is_outlier(adata, "pct_counts_mt", 5) | (
        adata.obs["pct_counts_mt"] > pct_mit_cutoff
    )
    mt_outlier_counts = adata.obs.mt_outlier.value_counts()
    mt_outlier_counts

    # Identify the filtered-out cells
    filtered_out_cells = adata.obs[(adata.obs.outlier) | (adata.obs.mt_outlier)].copy()
    filtered_out_cells
    # Save the filtered-out cells to CSV
    # filtered_out_cells.to_csv(out_directory / "filtered_out_cells.csv")
    # print(f"Saved {filtered_out_cells.shape[0]} filtered-out cells to 'filtered_out_cells.csv'.")

    # printing value for counts table
    mt_outlier_true_count = mt_outlier_counts.get(
        True, 0
    )  # Get count of True, default to 0 if not present
    print(mt_outlier_true_count)

    print(f"Total number of cells: {adata.n_obs}")
    total_cells = print(adata.n_obs)
    adata = adata[(~adata.obs.outlier) & (~adata.obs.mt_outlier)].copy()
    filt_total_cells = print(adata.n_obs)
    print(f"Number of cells after filtering of low quality cells: {adata.n_obs}")

    # filtered cell count
    cells_filt = adata.n_obs

    # create a table (DataFrame)
    data = {
        "sample_id": [sample_name],
        "raw_cell_count": [cells_raw],
        "filt_cell_count": [cells_filt],
        "outlier_count": [outlier_true_count],
        "mt_outlier_count": [mt_outlier_true_count],
    }

    df_counts = pd.DataFrame(data)

    # save table as csv
    df_counts.to_csv(out_directory / "qc_counts.csv")

    p6 = sc.pl.scatter(
        adata, "total_counts", "n_genes_by_counts", color="pct_counts_mt"
    )
    ### save p6

    ### removal of soublets using scrublet
    #########
    # Why is most of this commented out vm11?
    #########
    print("Sim doublet ratio:", sim_doublet_ratio)
    threshold = 0.7
    # sc.external.pp.scrublet(adata, sim_doublet_ratio=sim_doublet_ratio, threshold=threshold)
    # sc.pp.scrublet(adata)
    # sc.external.pp.scrublet(adata)

    # sc.external.pl.scrublet_score_distribution(adata)
    # adata.obs.predicted_doublet.value_counts()
    # adata = adata[~adata.obs.predicted_doublet]

    ### log normalisation

    adata.layers["counts"] = adata.X.copy()
    sc.pp.normalize_total(adata, target_sum=target_sum)

    sc.pp.log1p(adata)

    adata.raw = adata
    adata.layers["logcounts"] = adata.X.copy()

    sc.pp.highly_variable_genes(adata, n_top_genes=n_top_genes)

    ## scaling data is time consuming.. shall we inclue this?
    # sc.pp.scale(adata)

    ###########
    # AVOIDING IDENTIFICATION OF HIGHLY VARIABLE FEAUTRES (FEATURE SELECTION)
    ###########

    ## dimensional reduction

    # PCA
    sc.pp.pca(adata, use_highly_variable=True, n_comps=n_comps)

    ax = sns.scatterplot(
        data=adata.var, x="means", y="dispersions", hue="highly_variable", s=5
    )
    ax.set_xlim(None, 1.5)
    ax.set_ylim(None, 3)
    plt.show()
    ### save pca1

    reqCols = ["n_genes_by_counts", "total_counts", "pct_counts_mt"]
    sc.pl.pca_scatter(adata, color=reqCols)
    ### save pca2

    ## kNN, clustering and UMAP
    # neighbours (incl. leiden)

    sc.pp.neighbors(adata, n_pcs=n_pcs)

    sc.tl.leiden(adata, resolution=resolution)

    ##UMAP
    sc.tl.umap(adata, min_dist=min_dist, spread=spread)
    reqCols.extend(["leiden"])
    reqCols
    # ['n_genes_by_counts', 'total_counts', 'pct_counts_mt', 'leiden']

    sc.pl.umap(adata, color=reqCols, ncols=3)
    ### save umap

    ## Save csv of filtered genes/cutoffs

    ## Save single h5ad object (filtered)
    adata.write_h5ad(os.path.join(out_directory, sample_name + ".h5ad"))
