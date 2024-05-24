
%% Vclamp_analysis_singlecell.m but testing with a specific file.
%Basis for Vclamp_analysis_singlecell.m

% Created by Sayaka (Saya) Minegishi
% Contact: minegishis@brandeis.edu
% Date: May 24 2024

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
addpath '/Users/sayakaminegishi/MATLAB/Projects/VClamp_Analysis_SayaMinegishi'
%% Input:
filename = "/Users/sayakaminegishi/Documents/Birren Lab/Voltage clamp analysis/voltage clamp example data/2024_03_25_01_0000.abf";
sweepstoanalyze = [1:10];
%define region of interst to analyze (ms after start of recording)
starttime = 200; 
endtime = 1400; 

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

myVarnames = {'sweep number', 'ROI_StartTime(ms)', 'ROI_EndTime(ms)', 'baseline_current(pA)', 'peak_positive_amplitude(pA)', 'peak_negative_amplitude(pA)', 'synaptic_charge(pA*ms)'};

multipleVariablesTable= zeros(0,size(myVarnames, 2));
multipleVariablesRow = zeros(0,size(myVarnames, 2));
T= array2table(multipleVariablesTable, 'VariableNames', myVarnames); %stores info from all the sweeps in an abf file


%%%%%%%%% EXTRACT AND CLEAN DATA %%%%%%%%

%use Gunay's function to load data. Cengiz Gunay (2024). loadVclampAbf (https://www.mathworks.com/matlabcentral/fileexchange/29018-loadvclampabf), MATLAB Central File Exchange. Retrieved March 23, 2024.
%   time: Time vector for measurements [ms],
%   dt: Time step [ms],
%   data_i: Current traces (assumed [nA]),
%   data_v: Voltage traces (assumed [mV]),
%   cell_name: Extracted from the file name part of the path.

[time, dt, data_i, data_v, cell_name] = loadVclampAbf(filename); %using function by Gunay
si = dt*1000; %dt in microseconds

%go through each sweep, calculate area under curve

data_old = data_i; %includes all sweeps, pA (TODO: should i convert to nA?)
numsweeps = size(data_i,2); %get number of sweeps in data

%% denoise
data = smoothdata(data_old);


%%%%%%%%%%%%%%%%%%%%%%%%%%%
if(isempty(sweepstoanalyze))
    sweeps_to_analyze = 1:numsweeps; %specify the sweeps to analyze! 1:numsweeps to analyze all sweeps in file.
else
    sweeps_to_analyze = sweepstoanalyze;
end

synaptic_charge = zeros(1,length(numsweeps)); %array to store the total synaptic charge per sweep. aka area under curve for each sweep

for i = 1:numel(sweeps_to_analyze)

    sweepnumber = sweeps_to_analyze(i);
    sweep_data_whole = data(:,sweepnumber); %trace for the sweep to analyze
   
    %sweep_data = detrend(sweep_data, 1) + sweep_data(1); %Correct baseline - detrend shifts baseline to 0. TODO: maybe don't include.
    
    baseline_current = sweep_data_whole(1); 

   
    %find indices for time closest to specified start and end times
    [~, starttime_idx] = min(abs(time-starttime));
    [~, endtime_idx] = min(abs(time-endtime));

   
    sweep_data_roi = sweep_data_whole(starttime_idx:endtime_idx); %region of interest to analyze
    sweep_data_roi_xvals = time(starttime_idx:endtime_idx); %real time, in ms

    %calculate synaptic charge for the whole regionof interest
   
    synaptic_charge = trapz(sweep_data_roi) - trapz(baseline_current); %calculate synaptic charge (area under curve) for this sweep (pC). abs() can be used to make all negatives positive

    % detect peaks in both directions
    [pks, pklocs] = findpeaks(sweep_data_roi); %outward current peaks. gets indexes
    [troughs,trlocs] = findpeaks(-sweep_data_roi); %inward current peaks. gets indexes

    %peak positive amplitude
    ppa = max(sweep_data_roi) - baseline_current;

    %peak negative amplitude
    pna = min(sweep_data_roi) - baseline_current;

    %add to table
    multipleVariablesRow = {sweepnumber, starttime, endtime, baseline_current, ppa, pna, synaptic_charge};
    multipleVariablesTable = [multipleVariablesTable; multipleVariablesRow];
   
   
    end

    multipleVariablesTable = cell2table(multipleVariablesTable);
    multipleVariablesTable.Properties.VariableNames = myVarnames;
    disp(multipleVariablesTable); %final table
