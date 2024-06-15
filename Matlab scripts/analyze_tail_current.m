function tailCurrentTable = analyze_tail_current(filename, starttime, endtime)
%This function analyzes the properties of the tail current from a given
%data, with starttime and endtime being the start and end points (in ms) of
%the region of interest.

%put endtime = 0 if endtime is equal to the end of sweep.
%starttime = start time for curve-fitting
%endtime = end time for curve-fitting


% Created by Sayaka (Saya) Minegishi
% Contact: minegishis@brandeis.edu
% Last modified: June 14 2024

%%%%%%%%%%%%%

[time, dt, data_i, data_v, cell_name] = loadVclampAbf(filename); %using function by Gunay
si = dt*1000; %dt in microseconds

%go through each sweep, calculate area under curve

data_old = data_i; %includes all sweeps, pA (TODO: should i convert to nA?)
numsweeps = size(data_i,2); %get number of sweeps in data


%% denoise
data = smoothdata(data_old);

for i = 1:numel(data)

    sweepnumber = i;
    sweep_data = data(:,sweepnumber); %trace for the sweep to analyze
   %find indices for time closest to specified start and end times
    if(endtime == 0)
        endtime_idx = numel(time); %if endtime is not specified, take the end of the sweep as endtime
        endtime_roi = time(end);
    else
        [~, endtime_idx] = min(abs(time-endtime));
        endtime_roi = endtime;
    end


    [~, starttime_idx] = min(abs(time-starttime));
   
   
    sweep_data_roi = sweep_data(starttime_idx:endtime_idx); %region of interest to analyze
    sweep_data_roi_xvals = time(starttime_idx:endtime_idx); %real time, in ms

    sweep_data_indices = 1:numel(sweep_data_roi);

    f0 = fitExponential(sweep_data_indices.',sweep_data_roi); %fit exponential curve to region of interest. NOTE THIS IS THE CURVE AFTER starttime!
    %display fitted information
    display("sweep " + i)
    display(f0)

end

end
