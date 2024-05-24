function V_clamp_batchAnalysis(outputfile, starttime, endtime, selectedsweeps)

%performs analysis on V-clamp traces gives a table with the properties
%of each cell, with the last row being the AVERAGE of all the cells.

%outputfile = name of output excel file
%starttime = start time of region to analyze
%endtime = end time of region to analyze (ms)
%selectedsweeps = vector containing sweep numbers to analyze.


%does not analyze the command waveform (limitation of abfload), so please
%access the command waveform from another software (until I implement
%python code for it into this program).


% Original script by: Sayaka (Saya) Minegishi
% Contact: minegishis@brandeis.edu
% Date: May 24 2024


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
currentFolder = pwd;
mkdir tempdata %make a new folder to store the data files selected

%% define the excel file name 
filenameExcelDoc = fullfile(currentFolder, filesep, outputfile); %default file name

%% allow user to select files
[filename,pathname] = uigetfile('*.abf',...
    'Select One or More Files', ...
    'MultiSelect', 'on'); %prompt user to select multiple files

%move selected data to folder temporarily
pdest   = fullfile(currentFolder, filesep, 'tempdata');

if isequal(filename,0) || isequal(pathname,0)
    disp('User pressed cancel');
else
    if isa(filename, "char")  %if only one file
       
        sourceFile = fullfile(pathname, filename);
        destFile   = fullfile(pdest, filename);
        copyfile(sourceFile, destFile);

    else %if multiple files selected. TODO: FIX!!!!
        
        for k = 1:numel(filename)
            sourceFile = fullfile(pathname, filename{k});
            destFile   = fullfile(pdest, filename{k});
            copyfile(sourceFile, destFile);

        end
    end

end

%% analyze
tempDir = pdest;
% Start loading files
filesNotWorking = []; % List of files with errors
list = dir(fullfile(tempDir, '*.abf'));
file_names = {list.name}; % List of all abf file names in the directory

myVarnames = {'sweep number', 'ROI_StartTime(ms)', 'ROI_EndTime(ms)', 'baseline_current(pA)', 'peak_positive_amplitude(pA)', 'peak_negative_amplitude(pA)', 'synaptic_charge(pA*ms)'};

multipleVariablesTable= zeros(0,size(myVarnames, 2));
multipleVariablesRow = zeros(0,size(myVarnames, 2));
T= array2table(multipleVariablesTable, 'VariableNames', myVarnames); %stores info from all the sweeps in an abf file


for k = 1:numel(selectedsweeps)
    swp = selectedsweeps(k);

    for i = 1:numel(file_names)
        file_names{i} = fullfile(tempDir, file_names{i});
        fn = string(file_names{i});
        getgraph = 1; %put 0 if no graphs desired
        sweepdata = Vclamp_analysis_singlecell(fn, swp, starttime, endtime, getgraph);
        T=[T;sweepdata]; %summary table for each file: row = file, col = property
    
    end
    class(T)
    disp(T)

    %make a summary table to store averaged values across files for this
    %sweep
    summaryVarNames = {'sweep number', 'ROI_StartTime(ms)', 'ROI_EndTime(ms)', 'avg_baseline_current(pA)', 'avg_peak_positive_amplitude(pA)', 'avg_peak_negative_amplitude(pA)', 'avg_synaptic_charge(pA*ms)', 'n'};
    
    multipleVariablesTable2= zeros(0,size(summaryVarNames, 2));
    multipleVariablesRow2 = zeros(0,size(summaryVarNames, 2));
    summaryTable = array2table(multipleVariablesTable2, 'VariableNames', summaryVarNames); %stores info from all the sweeps in an abf file
    
    avg_baseline_current = mean(T{:,["baseline_current(pA)"]});
    avg_peak_positive_amplitude = mean(T{:,["peak_positive_amplitude(pA)"]});
    avg_peak_negative_amplitude = mean(T{:,["peak_negative_amplitude(pA)"]});
    avg_synaptic_charge = mean(T{:,["synaptic_charge(pA*ms)"]});

    multipleVariablesRow2 = {swp, starttime, endtime, avg_baseline_current,avg_peak_positive_amplitude, avg_peak_negative_amplitude, avg_synaptic_charge, size(T,1)};

    summaryTable = [summaryTable; multipleVariablesRow2];
    

end

disp(summaryTable)
writetable(summaryTable, outputfile, 'Sheet', 1); %export summary table to excel


end