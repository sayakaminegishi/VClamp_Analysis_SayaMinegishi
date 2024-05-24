function V_clamp_batchAnalysis(outputfile, starttime, endtime, sweeps)

%outputfile = name of output excel file
%starttime = start time of region to analyze
%endtime = end time of region to analyze (ms)
%sweeps = vector containing sweep numbers to analyze.

%performs analysis on V-clamp traces gives a table with the properties
%of each cell, with the last row being the AVERAGE of all the cells.

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
currentFolder = pwd; %path to current folder
pdest   = fullfile(currentFolder, filesep, 'tempdata');

if isequal(filename,0) || isequal(pathname,0)
    disp('User pressed cancel');
else
    if isa(filename, "char")  %if only one file
       
        sourceFile = fullfile(pathname, filename);
        destFile   = fullfile(pdest, filename);
        copyfile(sourceFile, destFile);

    else %if multiple files selected
        
        for k = 1:numel(filename)
            sourceFile = fullfile(pathname, filename{k});
            destFile   = fullfile(pdest, filename{k});
            copyfile(sourceFile, destFile);

        end
    end

end

%% analyze
tempDir = fullfile(currentFolder, 'tempdata', filesep); % Folder to load data

% Start loading files
filesNotWorking = []; % List of files with errors
list = dir(fullfile(tempDir, '*.abf'));
file_names = {list.name}; % List of all abf file names in the directory

for i = 1:numel(file_names)
    file_names{i} = fullfile(tempDir, file_names{i});
    fn = string(file_names{i});
    getgraph =1; %get graph. MODIFY TO 0 IF NO GRAPH IS DESIRED.
    multipleVariablesTable= Vclamp_analysis_singlecell(fn, sweeps, starttime, endtime, getgraph);

end

%% EXTRACT SWEEP-SPECIFIC DATA


end