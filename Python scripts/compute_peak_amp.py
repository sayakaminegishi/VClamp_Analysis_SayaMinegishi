''' PEAK CURRENT ANALYSIS - AUC and AMP
computes peak amplitude & area under curve for the greatest current step, for a specified protocol (with vsteps), and compares (gives avg) across multiple vclamp files.
#can be used to get average peak current properties for one strain. Can be ran 2 times to compare differences between two strains.

Created by: Sayaka (Saya) Minegishi
Contact: minegishis@brandeis.edu
Last modified: June 17 2024
'''
import numpy as np
import scipy.optimize
import scipy.signal
import matplotlib.pyplot as plt
import pyabf
import pandas as pd
import traceback
import logging
from PyQt5.QtWidgets import QApplication, QFileDialog

# Function to apply low-pass filter
def low_pass_filter(trace, SampleRate, cutoff=300, order=5):
    nyquist = 0.5 * SampleRate
    normal_cutoff = cutoff / nyquist
    b, a = scipy.signal.butter(order, normal_cutoff, btype='low', analog=False)
    filtered_trace = scipy.signal.filtfilt(b, a, trace)
    return filtered_trace


######### Ask user input (automatic - no need to change any code here) #########
app = QApplication([])
options = QFileDialog.Options()
file_paths, _ = QFileDialog.getOpenFileNames(None, "Select files", "", "ABF Files (*.abf);;All Files (*)", options=options)

print(f"Selected files: {file_paths}")

# Ask protocol type
protocolname = str(input("Enter the protocol type - Henckels or Bradley: "))

# Define peak time
if protocolname == "Henckels":
    starttime = 0.08
    endtime = 0.5810
elif protocolname == "Bradley":
    starttime = 0.0967
    endtime = 0.5963


filesnotworking = []

# Initialize summary table for recording data
columns = ['Filename', 'Peak_amplitude(pA)', 'Input_voltage(mV)','AreaUnderCurve(pA*mV)']  # column headers
df = pd.DataFrame(columns=columns)  # create an empty dataframe with the specified columns


for file in file_paths:
    try:
        print("\nWorking on " + file)

        abfdata = pyabf.ABF(file)
        swp = len(abfdata.sweepList)-1 #analyze the last sweep
        abfdata.setSweep(swp)
        
        # Visualize data
        plt.figure()
        plt.plot(abfdata.sweepX, abfdata.sweepY, color="orange")
        plt.xlabel('Time (s)')
        plt.ylabel('Current (pA)') 
        plt.title('Original Data')
        plt.legend() 

        # Extract sweep data and convert them to arrays
        time = np.array(abfdata.sweepX)
        trace = np.array(abfdata.sweepY)  # Current values
        inputv = np.array(abfdata.sweepC)
        SampleRate = abfdata.dataRate  # sample rate in total samples per second per channel
        baseline = trace[0]

        # Denoise the trace
        denoised_trace = low_pass_filter(trace, SampleRate)

        # Get peak amplitude
        mask1 = (time >= starttime) & (time <= endtime)
        filtered_values = denoised_trace[mask1]  # trace values, for the hyperpolarizing step
        filtered_time = time[mask1]

        peak_val = np.max(filtered_values)  #peak current
        index_of_peak = np.argmax(filtered_values) 
        peak_loc = filtered_time[index_of_peak]  

        peakamp = peak_val - baseline
        areaundercurve_dep = np.trapz(filtered_values, filtered_time) #area under the curve
        vAtPeak = inputv[index_of_peak] #input voltage at the time of the peak

        if peakamp is not None and areaundercurve_dep is not None and vAtPeak is not None:
            # Add filename, peakamp and areaundercurve, and voltage input to summary table
           
            new_row = {'Filename': file, 'Peak_amplitude(pA)': peakamp, 'Input_voltage(mV)': vAtPeak, 'AreaUnderCurve(pA*mV)': areaundercurve_dep}
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    except Exception as e:
        filesnotworking.append(file)
        logging.error(traceback.format_exc())  # log error

# Get summary data for the cell
print(df)  # show the recorded data

print("\nMean of each column:")

mean_a = df['Peak_amplitude(pA)'].mean()
mean_b = df['Input_voltage(mV)'].mean()
mean_c = df['AreaUnderCurve(pA*mV)'].mean()

print("Mean peak amplitude(pA): " + str(mean_a))
print("Mean Input_voltage(mV): " + str(mean_b))
print("Mean area under curve(mV*pA): " + str(mean_c))


# Show files not working
string = ','.join(str(x) for x in filesnotworking)
print("Files not working:" + string)


