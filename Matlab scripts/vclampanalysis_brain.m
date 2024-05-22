% Vclamp_analysis_singlecell.m but testing with a specific file

filename = "/Users/sayakaminegishi/Documents/Birren Lab/Voltage clamp analysis/voltage clamp example data/2024_03_25_01_0000.abf"
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
si = dt*1000; %dt in microseconds

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
    starttime=timenew(1);
    endtime = timenew(end);
    %extract the region of interest
    starttime_originalIdx = find(time==starttime); %convert start time in ms to index in sweep_data_whole
    endtime_originalIdx = find(time == endtime); %endtime in ms to index in sweep_data_whole
    transient_duration = 2643; %TODO: +/- 1? test these vals if it gives error
    transient_duration_ms = sampleunits_to_ms(si, transient_duration); %in ms
    
    starttime_newIdx = starttime_originalIdx-transient_duration; %start time on data with transient removed
    endtime_newIdx = endtime_originalIdx - transient_duration; %end time on data with transient removed
    baseline_current = sweep_data(1); 

    sweep_data_roi = sweep_data(starttime_newIdx:endtime_newIdx); %region of interest to analyze
    sweep_data_roi_xvals = timenew(starttime_newIdx:endtime_newIdx); %real time, in ms

    %calculate synaptic charge for the whole regionof interest
   
    synaptic_charge(i) = trapz(sweep_data_roi) - trapz(baseline_current); %calculate synaptic charge (area under curve) for this sweep (pC). abs() can be used to make all negatives positive

    % detect peaks in both directions
    [pks, pklocs] = findpeaks(sweep_data_roi); %outward current peaks. gets indexes
    [troughs,trlocs] = findpeaks(-sweep_data_roi); %inward current peaks. gets indexes

    %% edit from here
    %TODO: find all pts where signal reaches baseline (0) before and after
    %each peak to calculate AuC and duration for each signal

    AUCs_roi = zeros(1, (size(pks) + size(troughs))); %to store area under curve of each signal detected
    
    sweep_data_roi_shifted = sweep_data_roi - baseline_current; %shift everything to 0

    %find real x intercepts, where the graph comes back to baseline (in ms)
    back_to_baseline_locs = find_x_intercepts(sweep_data_roi_shifted, sweep_data_roi_xvals); %get real x ints
    back_to_baseline_locs_whole = back_to_baseline_locs + transient_duration_ms + starttime; %with respect to the whole trace, including the transients
    
    %find x intercepts (in indices)
    xints_idx = find_x_intercepts(sweep_data_roi_shifted, [1:numel(sweep_data_roi_shifted)]); %get real x ints
    
    %% create a table containing synaptic charge for each set of signals
    %initialize a new table with headers
    varnames_signals = {'Signal_start(ms)', 'Signal_end(ms)', 'AreaUnderCurve(ms*pA)', 'signal_duration(ms)'};
    signalsTable= zeros(0,size(varnames_signals, 2));
    signalsRow = zeros(0,size(varnames_signals, 2));
    signalsTable= array2table(signalsTable, 'VariableNames', varnames_signals); %stores info from all the sweeps in an abf file


    %find synaptic charge of each signal (defining synaptic charge as area
    %under curve below baseline)
    for z = 1:numel(xints_idx)-1
        intercept = xints_idx(z);
        
        y=sweep_data_roi_shifted(xints_idx>intercept&xints_idx<xints_idx(z+1) );
        x=xints_idx(xints_idx>intercept&xints_idx<xints_idx(z+1));
        
        area=trapz(x, y ); %area under curve for this signal
        AUCs_roi(z) = area;
        signalduration = find(xints_idx == max(xints_idx(z+1)-xints_idx)) - find(xints_idx == min(xints_idx-intercept)&xints_idx>intercept);

        %add a new row to the signalsTable. start and end times of signal
        %are with respect to whole trace, including transient
        signalsRow = {back_to_baseline_locs_whole(z), back_to_baseline_locs_whole(z+1),  AUCs_roi(z), signalDuration};
        signalsTable = [signalsTable; signalsRow];
    end

    

    % Display the table with AUCs
    disp("signals in sweep" + sweepnumber)
    disp(signalsTable);
