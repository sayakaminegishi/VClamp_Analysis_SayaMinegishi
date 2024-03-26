function [cleandata, cleantime] = remove_transient(data, time)

% this function removes the initial transient from a voltage clamp
% recording.
%[IN]
% data = original data to remove transient from
% time = vector contaning original time values
%[OUT]
% cleandata = data without the transient 
% cleantime= time vector without the transient (ms)

% Created by Sayaka (Saya) Minegishi
% minegishis@brandeis.edu
% 3/23/24

startpt = 2643; %index where transient ends
cleandata = data(startpt:end); %new data
cleantime = time(startpt:end); %new time vec

end