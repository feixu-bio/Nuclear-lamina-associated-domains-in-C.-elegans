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
