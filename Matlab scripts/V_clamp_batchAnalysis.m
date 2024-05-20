function V_clamp_batchAnalysis(datadir,outputfile)

%performs analysis on V-clamp traces gives a table with the properties
%of each cell, with the last row being the AVERAGE of all the cells.



% Original script by: Sayaka (Saya) Minegishi
% Contact: minegishis@brandeis.edu
% Date: May 20 2024


last_only = 0;

analysis_dir = fullfile(userpath, filesep, 'Projects', filesep, 'AP_AHP_Analysis_Iclamp_SayaMinegishi', filesep, 'analyses');

dirname = fullfile(userpath,filesep,  'Projects', filesep,'AP_AHP_Analysis_Iclamp_SayaMinegishi', filesep, 'data', filesep, datadir);


disp(['Now working on directory ' dirname])

%start loading files
filesNotWorking = []; %list of files with errors
list = dir('*.abf');
file_names = {list.name}; %list of all abf file names in the directory 
list = dir(fullfile(dirname, filesep, '*.abf'));%This script finds the firing properties of the FIRST AP ever detected
%from each cell in the directory, and exports the summary table as an excel
%file.
file_names = {list.name}; %list of all abf file names in the directory 
for i=1:numel(file_names),
    file_names{i} = fullfile(dirname, filesep, file_names{i});
end;

filenameExcelDoc = fullfile(analysis_dir, filesep, outputfile);

%table for summarizing burst properties
myVarnamesBursts = {'cell name', 'threshold(mV)', 'average_ISI(ms)', 'AP_frequency(Hz)', 'total_AP_count_in_cell', 'count_of_bursts', 'count_of_singletAPs', 'average_burst_duration(ms)', 'freq_bursts(Hz)'};

burstsTable= zeros(0,numel(myVarnamesBursts));
burstsTableRow = zeros(0, numel(myVarnamesBursts));
burstT= array2table(burstsTable, 'VariableNames', myVarnamesBursts); %stores info from all the sweeps in an abf file


%table for summarizing average of singlet AP properties from each cell
myVarnamesSing= {'threshold(mV)', 'duration(ms)', 'amplitude(mV)', 'AHP_amplitude(mV)', 'trough value (mV)', 'peak value(mV)',  'half_width(ms)', 'AHP_30_val(mV)', 'AHP_50_val(mV)', 'AHP_70_val(mV)', 'AHP_90_val(mV)', 'half_width_AHP(ms)', 'AHP_width_10to10%(ms)', 'AHP_width_30to30%(ms)', 'AHP_width_70to70%(ms)', 'AHP_width_90to90%(ms)'};

 %MAKE A TABLE WITH EMPTY VALUES BUT WITH HEADERS
% Define headers
headersSingT = {'spike_location(ms)', 'threshold(mV)', 'amplitude(mV)', 'AHP_amplitude(mV)', 'trough value (mV)', 'trough location(ms)', 'peak value(mV)', 'peak location(ms)', 'half_width(ms)', 'AHP_30_val(mV)', 'AHP_50_val(mV)', 'AHP_70_val(mV)', 'AHP_90_val(mV)', 'half_width_AHP(ms)', 'AHP_width_10to10%(ms)', 'AHP_width_30to30%(ms)', 'AHP_width_70to70%(ms)', 'AHP_width_90to90%(ms)', 'AHP_width_90to30%(ms)', 'AHP_width_10to90%(ms)'};
variableTypes = {'double', 'double', 'double', 'double',  'double',  'double',  'double',  'double',  'double',  'double',  'double',  'double',  'double',  'double',  'double',  'double',  'double',  'double' , 'double' , 'double' }; % Adjust the data types as needed

% Create an empty table with headers
singT = table('Size', [0, numel(headersSingT)], 'VariableNames', headersSingT, 'VariableTypes', variableTypes);
singT(:,[1,7]) = []; %delete irrelevant columns for averaged data
filesNotWorking = [];

for n=1:size(file_names,2)
        % filename = file_names(n); %file to work on
        % filename = filename{:};
        filename = string(file_names{n});
        disp([int2str(n) '. Working on: ' filename])
      try
        [singletAnalysisRow, T] = CMA_burst_analysis_feb17(filename); %get burst and singlet analysis for thsi cell
        burstT = [burstT; T];
        singT = [singT; singletAnalysisRow];
       
    catch
        fprintf('Invalid data in iteration %s, skipped.\n', filename);
        filesNotWorking = [filesNotWorking;filename];
    end
    
end

%add cell name column to singT
newcolumn = burstT(:,1); %first column of burstT
singT = [newcolumn, singT];

%%%%%%%%%%%%%%%%%%%%%%%%%

display(singT)
display(burstT)
display(filesNotWorking)
filesthatworkedcount = size(file_names,2) - size(filesNotWorking, 1);
display(filesthatworkedcount + " out of " + size(file_names,2) + " traces analyzed successfully.");

writetable(burstT, filenameExcelDoc, 'Sheet', 1); %export summary table for bursts to excel
writetable(singT, filenameExcelDoc, 'Sheet', 2); %export summary table for singlets to excel


end