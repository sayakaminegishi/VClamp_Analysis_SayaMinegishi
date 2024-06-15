function multipleVariablesTable = Vclamp_analysis_singlecell(filename, starttime, endtime, getgraph)

%Gives the voltage-clamp trace properties in a specified interval of time, from a specified file and specified sweeps of interest.
% usage example: to get current properties when performing voltage steps.

%starttime = time (in ms) at which region of analysis starts
%endtime = time (in ms) at which region of analysis ends. Put 0 if you want
%to analyze till the end of the trace.
%filename = full path to abf file
%getgraph = 0 if no graphical output desired, 1 if graph desired.

% Created by: Sayaka (Saya) Minegishi
% Contact: minegishis@brandeis.edu
% last updated: June 14 2024



%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

myVarnames = {'sweep number', 'ROI_StartTime(ms)', 'ROI_EndTime(ms)', 'baseline_current(pA)', 'peak_positive_amplitude_ROI(pA)', 'peak_negative_amplitude_ROI(pA)', 'max_current(pA)', 'loc_max_current(ms)', 'min_current(pA)', 'loc_min_current(ms)',  'synaptic_charge(pA*ms)'};
%"resistance(ohms)", "capacitance(pF)", "tau(ms)" - get on python

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

%display(data_v) - TODO: get this from python 


%%%%%%%%%%%%%%%%%%%%%%%%%%%

sweeps_to_analyze = [1:numsweeps];


synaptic_charge = zeros(1,length(numsweeps)); %array to store the total synaptic charge per sweep. aka area under curve for each sweep

for i = 1:numel(sweeps_to_analyze)

    sweepnumber = sweeps_to_analyze(i);
    sweep_data_whole = data(:,sweepnumber); %trace for the sweep to analyze
    %command_V_whole = data_v(:, sweepnumber); %trace for the command voltage

    %sweep_data = detrend(sweep_data, 1) + sweep_data(1); %Correct baseline - detrend shifts baseline to 0. TODO: maybe don't include.
    
    % %EXAMINE DATA
    % plot(time, command_V_whole)

    %%%%


    baseline_current = sweep_data_whole(1); 


   
    %find indices for time closest to specified start and end times
    if(endtime == 0)
        endtime_idx = numel(time); %if endtime is not specified, take the end of the sweep as endtime
        endtime_roi = time(end);
    else
        [~, endtime_idx] = min(abs(time-endtime));
        endtime_roi = endtime;
    end


    [~, starttime_idx] = min(abs(time-starttime));
   
   
    sweep_data_roi = sweep_data_whole(starttime_idx:endtime_idx); %region of interest to analyze
    sweep_data_roi_xvals = time(starttime_idx:endtime_idx); %real time, in ms
    %sweep_data_roi_cmdV = command_V_whole(starttime_idx:endtime_idx); %command voltage, in mV, for the region of interst

    %calculate synaptic charge for the whole regionof interest
   
    synaptic_charge = trapz(sweep_data_roi) - trapz(baseline_current); %calculate synaptic charge (area under curve) for this sweep (pC). abs() can be used to make all negatives positive

    % detect peaks in both directions
    [pks, pklocs] = findpeaks(sweep_data_roi); %outward current peaks. gets indexes
    [troughs,trlocs] = findpeaks(-sweep_data_roi); %inward current peaks. gets indexes

    %peak positive amplitude
    ppa = max(sweep_data_roi) - baseline_current;

    %peak negative amplitude
    pna = min(sweep_data_roi) - baseline_current;

     %max and min values
    [mxval, mxindex]= max(sweep_data_roi);
    mxindex = mxindex+ starttime_idx; %index of max current loc, with respect to the whole trace

    [mnval, mnindex] =min(sweep_data_roi);
    mnindex = mnindex+ starttime_idx; % index of min current loc, with respect to the whole trace

    mxtime = time(mnindex); %loc of max current in ROI, but with respect to the whole trace
    mntime = time(mnindex); %loc of min current in ROI, but with respect to the whole trace

   
  
    %add to table
   
    multipleVariablesRow = {sweepnumber, starttime, endtime_roi, baseline_current, ppa, pna, mxval, mxtime, mnval, mntime, synaptic_charge};
    multipleVariablesTable = [multipleVariablesTable; multipleVariablesRow];

   

    %give graph only if desired by user. Region of interest in yellow,
    %whole trace for the sweep in blue.
    if getgraph == 1
        % inspect signal
        %Plot the signal and the x-intercepts
        figure;
        plot(time, sweep_data_whole, 'b-', 'LineWidth', 1.5);
        hold on;
        plot(sweep_data_roi_xvals, sweep_data_roi, 'y-','LineWidth', 2);
        plot(time(mxindex), mxval, 'r+') %maximum point
        plot(time(mnindex), mnval, 'r+')
        xlabel('Time (ms)');
        ylabel('Current (pA)');
        title('Region of Interest');
        
        grid on;
    end
   
    end

    multipleVariablesTable = cell2table(multipleVariablesTable);
    multipleVariablesTable.Properties.VariableNames = myVarnames;
    disp(multipleVariablesTable); %final table
end