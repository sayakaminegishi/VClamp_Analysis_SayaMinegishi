function Vclamp_analysis_singlecell(filename, sweepstoanalyze, starttime, endtime)

%analyzes properties of a Voltage clamp recording for a single cell.
%Outputs a table with properties for each sweep, and then an average of
%each value at the end.

%sweepstoanalyze = a vector containig the sweep numbers to analyze. 
%starttime = time (in ms) at which region of analysis starts
%endtime = time (in ms) at which region of analysis ends

%% edit from here
myVarnames = {'sweep number', 'numSignals', 'avg_signal_duration(ms)', 'amplitude(pA)', 'min_value(pA)', 'synaptic_charge(pA*ms)'};

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

%go through each sweep, calculate area under curve

data = data_i*1e-3; %includes all sweeps,converted pA->nA
numsweeps = size(data_i,2); %get number of sweeps in data

if(isempty(sweepstoanalyze))
    sweeps_to_analyze = 1:numsweeps; %specify the sweeps to analyze! 1:numsweeps to analyze all sweeps in file.
else
    sweeps_to_analyze = sweepstoanalyze;
end

synaptic_charge = zeros(length(numsweeps)); %array to store the total synaptic charge per sweep. aka area under curve for each sweep

for i = 1:numel(sweeps_to_analyze)
    sweepnumber = sweeps_to_analyze(i);
    sweep_data_whole = data(:,sweepnumber); %trace for the sweep to analyze
   
    %clean data
    [sweep_data,timenew] = remove_transient(sweep_data_whole,time);
    %sweep_data = detrend(sweep_data, 1) + sweep_data(1); %Correct baseline - detrend shifts baseline to 0. TODO: maybe don't include.
    
    %extract the region of interest
    starttime_originalIdx = find(time==starttime); %convert start time in ms to index in sweep_data_whole
    endtime_originalIdx = find(time == endtime); %endtime in ms to index in sweep_data_whole
    transient_duration = 2643; %TODO: +/- 1? test these vals if it gives error
    
    starttime_newIdx = starttime_originalIdx-transient_duration; %start time on data with transient removed
    endtime_newIdx = endtime_originalIdx - transient_duration; %end time on data with transient removed
    baseline_current = sweep_data(1); 

    sweep_data_roi = sweep_data(starttime_newIdx:endtime_newIdx); %region of interest to analyze
    

    %calculate synaptic charge for the whole regionof interest
   
    synaptic_charge(i) = trapz(sweep_data_roi) - trapz(baseline_current); %calculate synaptic charge (area under curve) for this sweep (pC). abs() can be used to make all negatives positive

    % detect peaks in both directions
    [pks, pklocs] = findpeaks(sweep_data_roi); %outward current peaks. gets indexes
    [troughs,trlocs] = findpeaks(-sweep_data_roi); %inward current peaks. gets indexes

    %TODO: find all pts where signal reaches baseline (0) before and after
    %each peak to calculate AuC and duration for each signal




    %put into table
    multipleVariablesRow1= [sweepnumber, duration, synaptic_charge(i)];
   
    M1= array2table(multipleVariablesRow1, 'VariableNames', myVarnames1);
    T1 = [T1; M1]; %final table

    figure(1);
    plot(timenew, sweep_data);


end

%display table
display(T1)

%display total synaptic charge
total_synaptic_charge = sum(synaptic_charge); %total synaptic charge, Q, across all sweeps
display("The total synaptic charge is " + total_synaptic_charge + " pC")

writetable(T1, filenameExcelDoc, 'Sheet', 1); %export summary table to excel



end