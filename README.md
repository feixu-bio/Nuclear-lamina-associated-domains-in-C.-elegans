# Nuclear-lamina-associated-domains-in-C.-elegans

This repository contains custom analysis pipelines, ImageJ/Fiji macro scripts and CellProfiler project files accompanying the manuscript:

1. DamID_scRNAseq/folder: 
processes DamID and single-cell RNA-sequencing datasets. EMR-1_DamID-med1p-bound-bed-1707061998.txt contains the list of all 3113 10kb bins with a significant higher number of reads in Dam::EMR-1 versus GFP::Dam. Associated Panels: Figure 1, Figure S1.

2. spatial_intensity_analysis/folder: 
ImageJ/Fiji macro scripts (.ijm) for batch morphological and intensity quantifications: Heterochromatin radial distribution (peripheral ratio), nuclear-to-cytoplasmic ratio, Nuclear-signal intensity measurement. 
CellProfiler project files (.cpproj) calculating mean fractional radial intensity distributions for H3K9me and CPD signals.
Associated Panels: Figure 2, Figure 3, Figure 4, Figure S4, Figure S6, Figure S8, Figure S9, Figure S10A.
Execution Note: Requires CellProfiler to load the module settings.

3. pha-4-single-molecule-tracking/folder: 
Automated segmentation and 3D subnuclear positioning workflows to quantify the nearest distances of pha-4 DNA loci and nascent pha-4 transcription foci to the nuclear periphery. Cellpose_segment.py (Laurent Guerard, IMCF): Automated deep-learning-based nuclear boundary segmentation via the Cellpose framework.
Trackmate_LoG.py (Sebastien Herbert, IMCF): sub-pixel spot detection using the TrackMate Laplacian of Gaussian (LoG) detector. 
Execution Note: Scripts run inside the Fiji Python interpreter and interface with a local Python/Cellpose virtual environment. Associated Panels: Figure S1.

4. Directional_UVdamage/folder:
Standalone, CeT-pipeline-independent analysis scripts used for a paper's figures/analyses
(CPD intensity in *C. elegans* embryonic nuclei across a top/bottom UV-exposure gradient,
compared across `N2` (wt), `SM` (`cec-4, emr-1`), and `GW` (`met-2, set-25`) conditions).
Each script is its own argparse CLI (`python -m` or `python <script>.py -h`) and can be
run through the terminal.
# split_images.py
Given a folder of `.tif` image stacks, splits each stack along Z into "top" and "bottom"
portions (fraction size set by `-d/--denominator`, default halves) and writes them into
`top/`/`bottom/` subfolders under the output folder. Used to separate the top and bottom
halves of nuclei for the top-vs-bottom CPD comparison. Skips images whose output already
exists unless `-ow/--overwrite-output` is set.
# crop_images.py
Given a folder of images and an objects dataframe (`.csv`), crops each object out of its
source image and saves the crop to an output folder. Boundaries come either from a
`boundaries` column in the df, or (with `-f/--fixed-size`) from a fixed-size box centered on
each object's `centroid`; `-m/--margin` pads the crop, and `-k/--mask` restricts a mask crop
to only the pixels matching that object's `object_id`. Skips existing crops unless
`-ow/--overwrite-output` is set.
# regression_plots.py
Loads a nuclei summary dataframe and fits log-linear regressions of CPD mean intensity
(background-removed) against the number of nuclei above each nucleus (`nuclei_above_count`),
faceted by condition (`N2`/`SM`/`GW`). Produces an annotated regression figure (slope,
intercept, R², p-value per facet) saved as `regression.pdf`, fits an OLS interaction model
(condition × nuclei-above-count) to test whether slopes differ significantly between
conditions, runs pairwise slope comparisons (t-test contrasts, Bonferroni-corrected), and
saves the ANOVA table, pairwise comparisons, and OLS coefficients as `.csv` files in the
output folder.
# violin_plots.py
Loads a nuclei "halves" dataframe (expected to already carry a precomputed
`top_bottom_ratio` and `embryo_age_group` column), tags each row with its condition from the
image name, then plots the top/bottom CPD intensity ratio as a violin plot split by embryo
age group (`young` vs `old`), annotated with a Mann-Whitney significance test. Saves the
figure as `violins.pdf`.
