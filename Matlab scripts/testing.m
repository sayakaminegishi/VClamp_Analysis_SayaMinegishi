%this file shows how to use my vclamp analysis programs

% V_clamp_batchAnalysis("y.xlsx")

clear all
close all

%singlecell
filename = "/Users/sayakaminegishi/Documents/Birren Lab/Voltage clamp analysis/voltage clamp example data/2024_03_25_01_0000.abf";

multipleVariablesTable=Vclamp_analysis_singlecell(filename, [1:3], 200, 1000, 1); %vclamp analysis on a single abf file

%multiple cells
outputfile = 'samplemay24.xlsx';
starttime = 200;
endtime = 1000;
selectedsweeps= [1:5]
V_clamp_batchAnalysis(outputfile, starttime, endtime, selectedsweeps)
