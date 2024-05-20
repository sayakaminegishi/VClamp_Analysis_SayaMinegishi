function V_clamp_batchAnalysis(outputfile)

%outputfile = name of output excel file

%performs analysis on V-clamp traces gives a table with the properties
%of each cell, with the last row being the AVERAGE of all the cells.

%does not analyze the command waveform (limitation of abfload), so please
%access the command waveform from another software (until I implement
%python code for it into this program).


% Original script by: Sayaka (Saya) Minegishi
% Contact: minegishis@brandeis.edu
% Date: May 20 2024


last_only = 0;
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
end


%table for summarizing Vclamp properties
% amplitude is the amplitude of the current at the end of pulse. synaptic
% charge is the area under the curve.

%% TODO: EDIT FROM HERE BELOW
myVarnamesSing= {'duration(ms)', 'amplitude(pA)', 'min_value(pA)', 'synaptic_charge(pA*ms)'};

%MAKE A TABLE WITH EMPTY VALUES BUT WITH HEADERS
% Define headers
headersSingT= {'duration(ms)', 'amplitude(pA)', 'min_value(pA)', 'synaptic_charge(pA*ms)'};
variableTypes = {'double', 'double', 'double', 'double'};

% Create an empty table with headers
singT = table('Size', [0, numel(headersSingT)], 'VariableNames', headersSingT, 'VariableTypes', variableTypes);
singT(:,[1,7]) = []; %delete irrelevant columns for averaged data
filesNotWorking = [];

for n=1:size(file_names,2)

    filename = string(file_names{n});
    disp([int2str(n) '. Working on: ' filename])
    try
        [singletAnalysisRow, T] = CMA_burst_analysis_feb17(filename); %get burst and singlet analysis for thsi cell
        singT = [singT; singletAnalysisRow];

    catch
        fprintf('Invalid data in iteration %s, skipped.\n', filename);
        filesNotWorking = [filesNotWorking;filename];
    end

end

%add cell name column to singT
newcolumn = burstT(:,1); %first column of burstT
singT = [newcolumn, singT];


%%%%%%%%%%%%%%%%%
display(singT)
display(burstT)
display(filesNotWorking)
filesthatworkedcount = size(file_names,2) - size(filesNotWorking, 1);
display(filesthatworkedcount + " out of " + size(file_names,2) + " traces analyzed successfully.");

writetable(burstT, filenameExcelDoc, 'Sheet', 1); %export summary table for bursts to excel
writetable(singT, filenameExcelDoc, 'Sheet', 2); %export summary table for singlets to excel


end