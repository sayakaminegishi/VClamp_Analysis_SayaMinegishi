function deleteDirectory(directoryPath)

% Function: deletes a specific folder defined by directoryPath.
%directoryPath = full path of the directory that you want to delete
    
% Created based on code by Image Analyst: https://www.mathworks.com/matlabcentral/answers/344284-how-do-i-delete-the-contents-of-a-folder#answer_270366
% Modified by: Sayaka (Saya) Minegishi | minegishis@brandeis.edu 
% last updated: May 25 2024

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%first empty the contents of the folder
    
    myFolder = directoryPath;
    % Check to make sure that folder actually exists.  Warn user if it doesn't.
    if ~isdir(myFolder)
      errorMessage = sprintf('Error: The following folder does not exist:\n%s', myFolder);
      uiwait(warndlg(errorMessage));
      return; %get out of this program
    end

    % Get a list of all files in the folder with the desired file name pattern.
    filePattern = fullfile(myFolder, '*'); % Change to whatever pattern you need.
    theFiles = dir(filePattern);
    for k = 1 : length(theFiles)
      baseFileName = theFiles(k).name;
      fullFileName = fullfile(myFolder, baseFileName);
      %fprintf(1, 'Now deleting %s\n', fullFileName);
      delete(fullFileName);
    end

    rmdir('tempdata'); %remove folder
    
end