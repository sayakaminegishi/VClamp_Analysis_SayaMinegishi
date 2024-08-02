# VClamp_Analysis_SayaMinegishi
Original matlab and python scripts for automatic analysis of voltage clamp traces.

Note that some info in the headers are misleading because I reused some of the scripts for different analyses and I had no time to update the header info, I apologize. 

Created by Sayaka (Saya) Minegishi
minegishis@brandeis.edu

## Description of each Python script
Navigate to 'final' folder under python scripts. Header shows description.

* PercentChangeAmpAnalysis.py: Conducts Two-way ANOVA for 

## Description of each Matlab script

From Scripts folder, 

**"how_to_use.m"** - example script that demonstrates how to use my scripts.

**"V_clamp_batchAnalysis.m"** - Batch analysis of 1 or more voltage-clamp traces, for a specified interval of time and sweep(s). Gives area under curve (synaptic charge), baseline current, and amplitudes. No need to edit anything. Just click Run.  

**Vclamp_analysis_singlecell.m** - Vclamp trace analysis for a specified region of interest (defined by start and end times in ms), for selected sweeps, for a single specified file (file must be specified at the beginning of script). 


