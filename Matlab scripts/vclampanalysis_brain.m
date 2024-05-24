%TODO: ask Dr Van Hooser how to calculate area under signal curve

% Vclamp_analysis_singlecell.m but testing with a specific file
addpath '/Users/sayakaminegishi/MATLAB/Projects/VClamp_Analysis_SayaMinegishi'

filename = "/Users/sayakaminegishi/Documents/Birren Lab/Voltage clamp analysis/voltage clamp example data/2024_03_25_01_0000.abf";
sweepstoanalyze = [1:10];
%define region of interst to analyze (ms after start of recording)
starttime = 200; 
endtime = 1400; 

%%%%%%%%%%%%%%%%%%%%%%

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

data_old = data_i; %includes all sweeps, pA (TODO: should i convert to nA?)
numsweeps = size(data_i,2); %get number of sweeps in data

%% denoise
data = smoothdata(data_old);

% %% inspect signal
% % Plot the signal and the x-intercepts
% figure(100);
% plot(time, data, 'b-', 'LineWidth', 1.5);
% hold on;
% plot(time, datanew, 'r-');
% xlabel('x');
% ylabel('y');
% title('smoothing data');
% legend('Original signal', 'De-noised');
% grid on;
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

    % starttime_idx = find(time == starttime); %index corresponding to start time. TODO: HOW TO FIND CLOSEST VALUE TO THIS PT
    % endtime_idx = find(time == endtime);

    %find indices for time closest to specified start and end times
    [~, starttime_idx] = min(abs(time-starttime));
    [~, endtime_idx] = min(abs(time-endtime));

   
    sweep_data_roi = sweep_data_whole(starttime_idx:endtime_idx); %region of interest to analyze
    sweep_data_roi_xvals = time(starttime_idx:endtime_idx); %real time, in ms

    %calculate synaptic charge for the whole regionof interest
   
    synaptic_charge(i) = trapz(sweep_data_roi) - trapz(baseline_current); %calculate synaptic charge (area under curve) for this sweep (pC). abs() can be used to make all negatives positive

    % detect peaks in both directions
    [pks, pklocs] = findpeaks(sweep_data_roi); %outward current peaks. gets indexes
    [troughs,trlocs] = findpeaks(-sweep_data_roi); %inward current peaks. gets indexes

    numSignals = numel(pks) + numel(troughs); %total no. of signals detected

    AUCs_roi = zeros(1, numSignals); %to store area under curve of each signal detected
    
    sweep_data_roi_shifted = sweep_data_roi - baseline_current; %shift everything to 0

    %find real x intercepts, where the graph comes back to baseline (in ms)
    back_to_baseline_locs_whole = find_x_intercepts(sweep_data_roi_xvals,sweep_data_roi_shifted); %get real x ints
   
    %find x intercepts (in indices)
    xints_real = find_x_intercepts(sweep_data_roi_xvals, sweep_data_roi_shifted); %get real x ints
    xints_idx = ms_to_sampleunits(si, xints_real);
    
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
        
       %% TODO: GET HELP

       x = [xints_real(z):dt:xints_real(z+1)];
       x_i = ms_to_sampleunits(si,x);
        area=trapz(x_i, sweep_data_roi_shifted); %area under curve for this signal
        AUCs_roi(z) = area; %in indices*yunit
       


        
        signalDuration = back_to_baseline_locs_whole(z+1) - back_to_baseline_locs_whole(z);
        if signalDuration <=0 
            continue; %move onto next sweep. %TODO: ASK BEST WAY TO DO THIS 
        else
       
        %add a new row to the signalsTable. start and end times of signal
        %are with respect to whole trace, including transient
        signalsRow = {back_to_baseline_locs_whole(z), back_to_baseline_locs_whole(z+1),  AUCs_roi(z), signalDuration};
        signalsTable = [signalsTable; signalsRow];
    end

    end

    % Display the table with AUCs
    disp("signals in sweep" + sweepnumber)
    disp(signalsTable);
end