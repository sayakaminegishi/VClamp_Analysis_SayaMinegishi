%this file shows how to use my vclamp analysis programs

% Created by Sayaka (Saya) Minegishi
% contact: minegishis@brandeis.edu
% last modified: may 25 2024

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% V_clamp_batchAnalysis("y.xlsx")

clear all
close all

%singlecell analysis. put endtime = 0 if you want to analyze till the end
%of the sweep.

filename = "/Users/sayakaminegishi/Documents/Birren Lab/Voltage clamp analysis/voltage clamp example data/2024_03_25_01_0000.abf";

multipleVariablesTable=Vclamp_analysis_singlecell(filename, 0, 0, 1); %vclamp analysis on a single abf file


%multiple cells batch analysis - gives average for each sweep
outputfile = 'samplemay24.xlsx';
starttime = 200;
endtime = 1000;
selectedsweeps= [1:5]
V_clamp_batchAnalysis(outputfile, starttime, endtime, selectedsweeps)
