# FINAL - this program fits an exponential curve to the tail current in a specified voltage-clamp trace.
# Created by Sayaka (Saya) Minegishi, adjustments made by ChatGPT. 
# June 16 2024

import numpy as np
import scipy.optimize
import matplotlib.pyplot as plt
import pyabf
import pandas as pd
import traceback
import logging

##### USER-DEFINED INPUT DATA ############
filepath = "/Users/sayakaminegishi/Documents/Birren Lab/CaCC project/DATA_Ephys/2024_06_06_01_0003.abf"  # file to analyze
starttime = 0.6  # start of the hyperpolarizing step leading to the tail current (includes the part BEFORE trough)
endtime = 1.5  # end of tail current, ie the hyperpolarizing step (sec)

######################################
# Function to analyze the tail current (from trough to end of tail)
def analyze_tail(time, trace, trough, HypEnd, sweep, SampleRate):
    def monoExp(x, a, b, c):
        return a * np.exp(b * x) + c
    
    mask = (time >= trough) & (time <= HypEnd)  # region to analyze - from trough to end of tail

    # Fit exponential model to part of tail after trough with initial guess and bounds
    initial_guess = [1, -1, 1]
    bounds = ([-np.inf, -np.inf, -np.inf], [np.inf, 0, np.inf])  # b should be negative for decay

    params, cv = scipy.optimize.curve_fit(monoExp, time[mask], trace[mask], p0=initial_guess, bounds=bounds)
    a, b, c = params
    tauSec = -1 / b  # Tau (time constant)

    # Determine quality of the fit
    squaredDiffs = np.square(trace[mask] - monoExp(time[mask], *params))
    squaredDiffsFromMean = np.square(trace[mask] - np.mean(trace[mask]))
    rSquared = 1 - np.sum(squaredDiffs) / np.sum(squaredDiffsFromMean)
    print(f"R² = {rSquared}")

    # Visualize fitted curve
    plt.scatter(time, trace, label="data")
    x_fit = np.linspace(time[mask].min(), time[mask].max(), 1000)  # x values for line of best fit
    y_fit = monoExp(x_fit, *params)  # y values for fitted curve
    plt.plot(x_fit, y_fit, c="red", label="fit")
    plt.axvline(x = trough, color = 'b', linestyle = 'dashed',  label = 'Trough')
    plt.axvline(x = HypEnd, color = 'b', linestyle = 'dashed',  label = 'End of hyperpolarization')
 
    plt.legend()
    plt.show()

    # Inspect the parameters
    print(f"Sweep {sweep}")
    print(f"Y = {a} * exp({b} * x) + {c}")
    print(f"Tau = {tauSec * 1e6} µs")

    return a, b, c

########### MAIN PROGRAM ################
abfdata = pyabf.ABF(filepath)

print(abfdata)  # gives info about abfdata, such as no. of sweeps, channels, duration

# Initialize summary table for recording data
columns = ['sweep_number', 'a', 'b', 'c']  # column headers
df = pd.DataFrame(columns=columns)  # create an empty dataframe with the specified columns

# Run - iterate over all sweeps in file
for i in abfdata.sweepList:
    abfdata.setSweep(i)
    #plot data
    plt.figure()
    plt.plot(abfdata.sweepX, abfdata.sweepY, color="orange")
    # Add labels and title
    plt.xlabel('Time (s)')
    plt.ylabel('Current (pA)')
    plt.title('Exponential Fit: Averaged Line of Best Fit')
    plt.legend()

    # Extract sweep data and convert them to arrays
    time = np.array(abfdata.sweepX)
    trace = np.array(abfdata.sweepY)  # Current values
    SampleRate = abfdata.dataRate  # sample rate in total samples per second per channel

    # Get trough
    mask1 = (time >= starttime) & (time <= endtime)
    filtered_values = trace[mask1]  # trace values, for the hyperpolarizing step
    filtered_time = time[mask1]

    trough_val = np.min(filtered_values)  # minimum value of tail current, in mV
    index_of_min = np.argmin(filtered_values)  # find the index of the minimum value
    trough_loc = filtered_time[index_of_min]  # trough location, in seconds

    try:
        afound, bfound, cfound = analyze_tail(time, trace, trough_loc, endtime, i, SampleRate)
        # Add sweep, a, b, c to the summary table
        new_row = {'sweep_number': i, 'a': afound, 'b': bfound, 'c': cfound}
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    except Exception as e:
        logging.error(traceback.format_exc())  # log error

############# Get summary data for the cell ################

# Get summary data
print("Recorded fit, y = a * exp(b * x) + c")
print(df)  # show the recorded data

# # Calculate the mean of each column
# column_means = df.mean()

# # Print the means
# print("\nMean of each column for this cell:")
# print(column_means)  # use column_means['var'] to access specific column val

# mean_a = column_means['a']
# mean_b = column_means['b']
# mean_c = column_means['c']

# # Print the averaged line of best fit
# print(f"Averaged line of best fit: y = {mean_a} * exp({mean_b} * x) + {mean_c}")

# # Plot the resulting curve
# x_values = np.linspace(starttime, endtime, 1000)
# y_values = mean_a * np.exp(mean_b * x_values) + mean_c

# plt.figure(figsize=(10, 6))
# plt.plot(x_values, y_values, label=f"y = {mean_a:.2f} * exp({mean_b:.2f} * x) + {mean_c:.2f}", color='red')

# # Add labels and title
# plt.xlabel('Time (s)')
# plt.ylabel('Current (pA)')
# plt.title('Exponential Fit: Averaged Line of Best Fit')
# plt.legend()
# plt.grid(True)
# plt.show()
