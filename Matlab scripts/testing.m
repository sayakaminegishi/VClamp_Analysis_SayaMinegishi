clear all
close all

%singlecell analysis
%filename = "/Users/sayakaminegishi/Documents/Birren Lab/Voltage clamp analysis/voltage clamp example data/2024_03_25_01_0000.abf";
filename = "/Users/sayakaminegishi/Documents/Birren Lab/CaCC project/DATA_Ephys/2024_06_06_01_0007.abf";

multipleVariablesTable=Vclamp_analysis_singlecell(filename, 0, 0, 1); %vclamp analysis on a single abf file

%tail current analysis
filename = "/Users/sayakaminegishi/Documents/Birren Lab/CaCC project/DATA_Ephys/2024_06_06_01_0007.abf";

starttime = 0.6*1000; %in ms
endtime = 1.6*1000;
tailCurrentTable = analyze_tail_current(filename, starttime, endtime)

%%%%%% abfload
[d,si,h]=abfload(filename,'info') %h = has header info
h.recChUnits %accessing channel info

 