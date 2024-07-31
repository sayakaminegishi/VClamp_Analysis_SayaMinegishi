filename = "2016_05_19_07_0002 (1).abf";
[time, dt, data_i, data_v, cell_name] = loadVclampAbf(filename);

%   time: Time vector for measurements [ms],
%   dt: Time step [ms],
%   data_i: Current traces (assumed [nA]),
%   data_v: Voltage traces (assumed [mV]),
%   cell_name: Extracted from the file name part of the path.
%

a = 4; %sweep to analyze
%data = data_i(:,1:a); %look at multiple sweeps at once!

data = data_i(:,a);
data = detrend(data, 1) + data(1); %Correct baseline - detrend shifts baseline to 0

figure(1);
plot(data)

test_spike = data(64149:71409); %select a region to analyze. data(start:finishindex)

figure(2)
plot(test_spike)

%analyze region
areaUnderCurve = trapz(test_spike) %in cacc project, compare AUC of TMEM16A tail currents during time interested (eg during hyperpolarization period)
