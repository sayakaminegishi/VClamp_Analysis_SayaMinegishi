% % filename = "2016_05_19_07_0002 (1).abf";
% % 
% % 
% % filenameExcelDoc = strcat('vclamp_synapticCharge1.xlsx');
% % 
% % myVarnames1= {'sweep_number', 'synaptic_charge (pC)'};
% % 
% % multipleVariablesTable= zeros(0,numel(myVarnames1));
% % multipleVariablesRow1 = zeros(0, numel(myVarnames1));
% % 
% % T1= array2table(multipleVariablesTable, 'VariableNames', myVarnames1); %stores info from all the sweeps in an abf file
% % 
% % %use Gunay's function to load data. Cengiz Gunay (2024). loadVclampAbf (https://www.mathworks.com/matlabcentral/fileexchange/29018-loadvclampabf), MATLAB Central File Exchange. Retrieved March 23, 2024.
% % %   time: Time vector for measurements [ms],
% % %   dt: Time step [ms],
% % %   data_i: Current traces (assumed [nA]),
% % %   data_v: Voltage traces (assumed [mV]),
% % %   cell_name: Extracted from the file name part of the path.
% % 
% % [time, dt, data_i, data_v, cell_name] = loadVclampAbf(filename); %using function by Gunay
% % 
% % %go through each sweep, calculate area under curve
% % 
% % data = data_v; % get stimulus info. 
pyabf = py.importlib.import_module('pyabf');

filename = "2024_03_25_01_0000.abf";
[d,si,h]=abfload(filename, 'info');
h
size(d)
filepath_this = "/Users/sayakaminegishi/Documents/Birren Lab/Voltage clamp analysis/voltage clamp example data/2024_03_25_01_0000.abf";

commandV = pyrunfile("get_command_Voltage.py","commandv",filepath1 = filepath_this) %get command voltage array