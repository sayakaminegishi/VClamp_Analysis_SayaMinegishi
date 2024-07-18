''' FINDS AVERAGE EXP MODEL FOR TAIL CURRENT ACROSS MULTIPLE FILES, FOR A GIVEN SWEEP.

This program fits an exponential model to the tail currents of one or more user-selected files (asked via popup window - no need to change code),
for a specific sweep, given its protocol name, and finds the average fitted curve across the files. 
Make sure that all files picked at one time are from the same protocol. 

Created by: Sayaka (Saya) Minegishi. Some modifiactions made by ChatGPT.
Contact: minegishis@brandeis.edu
Last modified: June 20 2024

'''
import os
import numpy as np
import scipy.optimize
import scipy.signal
import matplotlib.pyplot as plt
import pyabf
import pandas as pd
import traceback
import logging
from PyQt5.QtWidgets import QApplication, QFileDialog
from getFilePath import get_file_path # type: ignore
from get_tail_times import getStartEndTail
from remove_abf_extension import remove_abf_extension # type: ignore
from getTailCurrentModel import getExpTailModel

# Function to apply low-pass filter
def low_pass_filter(trace, SampleRate, cutoff=300, order=5):
    nyquist = 0.5 * SampleRate
    normal_cutoff = cutoff / nyquist
    b, a = scipy.signal.butter(order, normal_cutoff, btype='low', analog=False)
    filtered_trace = scipy.signal.filtfilt(b, a, trace)
    return filtered_trace


def monoExp(x, a, b, c):
    return a * np.exp(b * x) + c

# Function to analyze the tail current (from trough to end of tail)
def analyze_tail(time, trace, trough, HypEnd, SampleRate):
    
   
    
    mask = (time >= trough) & (time <= HypEnd)  # region to analyze - from trough to end of tail

    # Fit exponential model to part of tail after trough with initial guess and bounds
    initial_guess = [1, -1, 1]
    bounds = ([-np.inf, -np.inf, -np.inf], [np.inf, 0, np.inf])  # b should be negative for decay

    try:
        params, cv = scipy.optimize.curve_fit(monoExp, time[mask], trace[mask], p0=initial_guess, bounds=bounds, maxfev=10000)  # Increased maxfev
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

        return a, b, c, tauSec

    except RuntimeError as e:
        print(f"Error: {e}")
        return None, None, None

########## Ask user input (automatic - no need to change any code here) #########
app = QApplication([])
options = QFileDialog.Options()
file_paths, _ = QFileDialog.getOpenFileNames(None, "Select files", "", "ABF Files (*.abf);;All Files (*)", options=options)

print(f"Selected files: {file_paths}")

# Ask user to select a directory to save the Excel files
save_directory = QFileDialog.getExistingDirectory(None, "Select Directory to Save Excel Files", options=options)

if not save_directory:
    print("No directory selected. Exiting...")
    exit()

print(f"Selected save directory: {save_directory}")


# Ask sweep number to analyze
swp = int(input("Enter the sweep number to analyze: "))
protocolname = str(input("Enter protocol name: "))

starttime, endtime = getStartEndTail(protocolname,swp)
# # Define start and end times
# starttime = 0.6  # start of the hyperpolarizing step leading to the tail current (includes the part BEFORE trough)
# endtime = 1.5  # end of tail current, ie the hyperpolarizing step (sec)

filesnotworking = []

# Initialize summary table for recording data
columns = ['Filename', 'a', 'b', 'c']  # column headers
df = pd.DataFrame(columns=columns)  # create an empty dataframe with the specified columns

for file in file_paths:
    try:
        file_n = remove_abf_extension(file)
        print("\nWorking on " + file)

        abfdata = pyabf.ABF(file)
        num_channels = abfdata.channelCount
        if num_channels == 1:
            abfdata.setSweep(swp)
        else:
            abfdata.setSweep(sweepNumber= swp, channel= 1)

       
  
        
        # Visualize data
        plt.figure()
        plt.plot(abfdata.sweepX, abfdata.sweepY, color="orange")
        plt.xlabel('Time (s)')
        plt.ylabel('Current (pA)')
        plt.title('Exponential Fit: Averaged Line of Best Fit')
        plt.legend()

        # Extract sweep data and convert them to arrays
        time = np.array(abfdata.sweepX)
        trace = np.array(abfdata.sweepY)  # Current values
        SampleRate = abfdata.dataRate  # sample rate in total samples per second per channel

        # Denoise the trace
        denoised_trace = low_pass_filter(trace, SampleRate)

        # Get trough
        mask1 = (time >= starttime) & (time <= endtime)
        filtered_values = denoised_trace[mask1]  # trace values, for the hyperpolarizing step
        filtered_time = time[mask1]

        trough_val = np.min(filtered_values)  # minimum value of tail current, in mV
        index_of_min = np.argmin(filtered_values)  # find the index of the minimum value
        trough_loc = filtered_time[index_of_min]  # trough location, in seconds

        afound, bfound, cfound, tauSec = analyze_tail(time, denoised_trace, trough_loc, endtime, SampleRate)
        if afound is not None and bfound is not None and cfound is not None:
            # Add filename, a, b, c to the summary table
            new_row = {'Filename': file_n, 'a': afound, 'b': bfound, 'c': cfound}
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    except Exception as e:
        filesnotworking.append(file)
        logging.error(traceback.format_exc())  # log error

# Get summary data for the cell
print(df)  # show the recorded data

print("\nMean of each column for this cell:")

mean_a = df['a'].mean()
mean_b = df['b'].mean()
mean_c = df['c'].mean()

# Print the averaged line of best fit
print(f"Averaged line of best fit: y = {mean_a:.3e} * exp({mean_b:.2f} * x) + {mean_c:.2f}")

# Plot the resulting curve
x_values = np.linspace(starttime, endtime, 1000)
y_values = mean_a * np.exp(mean_b * x_values) + mean_c

plt.figure(figsize=(10, 6))
plt.plot(x_values, y_values, label=f"y = {mean_a:.2f} * exp({mean_b:.2f} * x) + {mean_c:.2f}", color='red')
plt.xlabel('Time (s)')
plt.ylabel('Current (pA)')
plt.title('Exponential Fit: Averaged Line of Best Fit for Sweep ' + str(swp))
plt.legend()
plt.grid(True)
plt.show()


# Export all the dataframes from all the files analyzed to a single Excel file
# Construct the file name
summary_excelname = os.path.join(save_directory, f"AvgTails_{protocolname}_sweep{swp}.xlsx")

# Use ExcelWriter to save the DataFrame to an Excel file
with pd.ExcelWriter(summary_excelname, engine='xlsxwriter') as writer:
    
    df.to_excel(writer, sheet_name=protocolname, index=False)

# Show files not working
string = ','.join(str(x) for x in filesnotworking)
print("Files not working:" + string)


########## FUNCTION FORM OF ABOVE SCRIPT - gives exponential fitted model for tail ##########################
def get_tail_model(time, denoised_trace, trough_loc, endtime, SampleRate):
    #starttail = start time of tail, endtail = end time of tail

    try:
        afound, bfound, cfound,tauSec = analyze_tail(time, denoised_trace, trough_loc, endtime, SampleRate)
        if afound is not None and bfound is not None and cfound is not None:
            
            # Print the averaged line of best fit
            print(f"Averaged line of best fit: y = {afound:.3e} * exp({bfound:.2f} * x) + {cfound:.2f}")

            # return resulting curve
            x_values = np.linspace(starttime, endtime, 1000)
            y_values = afound * np.exp(bfound * cfound) + mean_c

            return x_values, y_values

    except Exception as e:
        logging.error(traceback.format_exc())  # log error



