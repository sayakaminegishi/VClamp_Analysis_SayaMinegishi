function x_intercepts = find_x_intercepts(y_data, x_data)
%this function finds all the x intercepts of a given signal.

% xints = array of x intercepts in shifted_signal 

%created by: Sayaka (Saya) Minegishi
%contact: minegishis@brandeis.edu
%last updated: May 21 2024

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Find intervals where the signal crosses the x-axis
crossings = find(diff(sign(y_data)));

% Initialize array to hold x-intercepts
x_intercepts = [];

% Interpolate to find the precise x-intercepts
for i = 1:length(crossings)
    % Indices of the points around the crossing
    idx1 = crossings(i);
    idx2 = idx1 + 1;
    
    % x-values around the crossing
    x1 = x_data(idx1);
    x2 = x_data(idx2);
    
    % y-values around the crossing
    y1 = y_data(idx1);
    y2 = y_data(idx2);
    
    % Interpolate to find the x-intercept
    x_zero = interp1([y1, y2], [x1, x2], 0);
    
    % Store the result
    x_intercepts = [x_intercepts, x_zero];
end

% Display the x-intercepts
disp('X-intercepts:');
disp(x_intercepts);

% Plot the signal and the x-intercepts
figure;
plot(x_data, y_data, 'b-', 'LineWidth', 1.5);
hold on;
plot(x_intercepts, zeros(size(x_intercepts)), 'ro');
xlabel('x');
ylabel('y');
title('Signal with X-intercepts');
legend('Signal', 'X-intercepts');
grid on;
end