# calculates the average fitted curve for the tail currents in multiple cells for one specific sweep

import numpy as np
import scipy.optimize
import matplotlib.pyplot as plt
import pyabf
import pandas as pd
import traceback
import logging
import tkinter as tk
from tkinter import filedialog
from PyQt5.QtWidgets import QApplication, QFileDialog

########## Ask user input (automatic - no need to change any code here) #########
# #make user select data via open dialogue
# root = tk.Tk()
# root.withdraw()  # Hide the main window

# # Open file dialog and get the file paths
# file_paths = filedialog.askopenfilenames(title="Select files", filetypes=[("ABF files", "*.abf"), ("All files", "*.*")])
# print(f"Selected files: {file_paths}")


app = QApplication([])
options = QFileDialog.Options()
file_paths, _ = QFileDialog.getOpenFileNames(None, "Select files", "", "ABF Files (*.abf);;All Files (*)", options=options)

print(f"Selected files: {file_paths}")

#ask sweep number to analyze
swp = int(input("Enter the sweep number to analyze: "))

# #select protocol
# protocolnames = ['Bradley', 'Henckels']
# protocolnum = int(input("Enter the protocol type- 1) Bradley, 2) Henckels: "))
# print(f"You selected the {protocolnames[protocolnum]} protocol.")

#TODO: define start and end times for each protocol type using if/else
starttime = 0.6  # start of the hyperpolarizing step leading to the tail current (includes the part BEFORE trough)
endtime = 1.5  # end of tail current, ie the hyperpolarizing step (sec)

######################## DEFINE FUNCTIONS ###############

# Function to analyze the tail current (from trough to end of tail)
def analyze_tail(time, trace, trough, HypEnd, SampleRate):
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
    plt.legend()
    plt.show()

    # Inspect the parameters
    print(f"Y = {a} * exp({b} * x) + {c}")
    print(f"Tau = {tauSec * 1e6} µs")

    return a, b, c

########### MAIN PROGRAM ################
# Initialize summary table for recording data
columns = ['Filename', 'a', 'b', 'c']  # column headers
df = pd.DataFrame(columns=columns)  # create an empty dataframe with the specified columns


for file in file_paths:
    print("Working on " + file)

    abfdata = pyabf.ABF(file)
    print(abfdata)  # gives info about abfdata, such as no. of sweeps, channels, duration
    abfdata.setSweep(swp)
    
    #visualize data
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
        afound, bfound, cfound = analyze_tail(time, trace, trough_loc, endtime, SampleRate)
        # Add filename, a, b, c to the summary table
        new_row = {'filename': file, 'a': afound, 'b': bfound, 'c': cfound}
        df = df.append(new_row, ignore_index=True)
    except Exception as e:
        logging.error(traceback.format_exc())  # log error

############# Get summary data for the cell ################

# Get summary
print(df)  # show the recorded data

print("\nMean of each column for this cell:")

mean_a = df['a'].mean()
mean_b = df['b'].mean()
mean_c = df['c'].mean()

# Print the averaged line of best fit
print(f"Averaged line of best fit: y = {mean_a} * exp({mean_b} * x) + {mean_c}")

# Plot the resulting curve
x_values = np.linspace(starttime, endtime, 1000)
y_values = mean_a * np.exp(mean_b * x_values) + mean_c

plt.figure(figsize=(10, 6))
plt.plot(x_values, y_values, label=f"y = {mean_a:.2f} * exp({mean_b:.2f} * x) + {mean_c:.2f}", color='red')

# Add labels and title
plt.xlabel('Time (s)')
plt.ylabel('Current (pA)')
plt.title('Exponential Fit: Averaged Line of Best Fit for Sweep ' + str(swp))
plt.legend()
plt.grid(True)
plt.show()
