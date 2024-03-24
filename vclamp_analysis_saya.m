filename = "2016_05_19_07_0002 (1).abf";


filenameExcelDoc = strcat('vclamp_synapticCharge1.xlsx');

myVarnames1= {'sweep_number', 'synaptic_charge (pC)'};

multipleVariablesTable= zeros(0,numel(myVarnames1));
multipleVariablesRow1 = zeros(0, numel(myVarnames1));

T1= array2table(multipleVariablesTable, 'VariableNames', myVarnames1); %stores info from all the sweeps in an abf file

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

sweeps_to_analyze = 1:numsweeps; %specify the sweeps to analyze! 1:numsweeps to analyze all sweeps in file.

synaptic_charge = zeros(length(numsweeps)); %array to store the total synaptic charge per sweep. aka area under curve for each sweep

for i = 1:numsweeps
    sweep_data = data(:,i); %trace for the sweep to analyze
   
    %clean data
    [sweep_data,timenew] = remove_transient(sweep_data,time);
    sweep_data = detrend(sweep_data, 1) + sweep_data(1); %Correct baseline - detrend shifts baseline to 0

    %analyze region
    synaptic_charge(i) = trapz(sweep_data); %calculate synaptic charge (area under curve) for this sweep (pC). abs() can be used to make all negatives positive
   
    %put into table
    multipleVariablesRow1= [i, synaptic_charge(i)];
   
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







