function f0= fitExponential(x,y)

%This function fits an exponential curve to a given data using the
%Levenberg-Marquardt fitting algorithm, and plots the results.

%INPUTS:
%x = vector containing values for the x-axis
%y = vector containing values for the y axis

%OUTPUTS:
%exp_lm = results of the fit, with coefficients calculated with the Levenberg-Marquardt fitting algorithm. 
%gof_lm = goodness-of-fit statistics

% Created by Sayaka (Saya) Minegishi
% Contact: minegishis@brandeis.edu
% Last modified: June 14 2024

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% % [exp_lm,gof_lm] = fit(x,y,"exp2",Algorithm="Levenberg-Marquardt");
% % 
% % plot(exp_lm,x,y)
% % legend(["data","predicted value"])
% % xlabel("x")
% % ylabel("y")
% 
% 
% g = fittype('a-b*exp(-c*x)');
% f0 = fit(x,y,g,'StartPoint',[[ones(size(x)), -exp(-x)]\y; 1]);
% xx = linspace(1,8,50);
% plot(x,y,'o',xx,f0(xx),'r-');

% Define the model: y = a * exp(b * x)
model = fittype('a*exp(b*x)');


% Set bounds on the coefficients
lower_bounds = [0, -Inf];  % 'a' should be non-negative, no lower bound for 'b'
upper_bounds = [Inf, Inf];  % No upper bounds

% Initial guess for the coefficients
start_points = [1, 0.5];

% Fit options
fit_options = fitoptions('Method', 'NonlinearLeastSquares', ...
                         'StartPoint', start_points, ...
                         'Lower', lower_bounds, ...
                         'Upper', upper_bounds);

% Fit the model to data with options
fitresult = fit(x, y, model, fit_options);

% Display the fit results
disp(fitresult);

% Plot the fit
figure;
plot(fitresult, x, y);
title('Exponential Fit');
xlabel('x');
ylabel('y');

