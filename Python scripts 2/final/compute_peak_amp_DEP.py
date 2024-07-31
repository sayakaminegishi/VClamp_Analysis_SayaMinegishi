"""
PEAK CURRENT ANALYSIS - AUC and AMP
Computes peak amplitude & area under curve for the greatest current step, for a specified protocol (with vsteps), and compares (gives avg) across multiple vclamp files.
Can be used to get average peak current properties for one strain. Can be ran 2 times to compare differences between two strains.

This script gives the PEAK, not necessarily the steady-state current.

Works for Henckels & Bradley Protocols.

Created by: Sayaka (Saya) Minegishi
Contact: minegishis@brandeis.edu
Last modified: Jul 19 2024
"""

import numpy as np
import scipy.optimize
import scipy.signal
import matplotlib.pyplot as plt
import pyabf
import pandas as pd
import traceback
import logging
from PyQt5.QtWidgets import QApplication, QFileDialog, QInputDialog, QMessageBox
import os
from get_base_filename import get_base_filename
from get_tail_times import getDepolarizationStartEnd, getZoomStartEndTimes
from plotSweepsAndCommand import plotAllSweepsAndCommand
from showInstructions import showInstructions

def low_pass_filter(trace, SampleRate):
    cutoff=300
    order=5
    nyquist = 0.5 * SampleRate
    normal_cutoff = cutoff / nyquist
    b, a = scipy.signal.butter(order, normal_cutoff, btype='low', analog=False)
    filtered_trace = scipy.signal.filtfilt(b, a, trace)
    return filtered_trace

# Smooth the peaks at the start and end of depolarization and exclude them from analysis
def smooth_edges(trace, dep_time_seconds, SampleRate):
    dep_length = int(dep_time_seconds * SampleRate)  # Depolarization duration from seconds to indices
    smoothedTrace = np.copy(trace)  # Make a duplicate of the original trace

    # Smooth the beginning uncompensated transient
    smoothedTrace[:dep_length] = np.linspace(trace[0], trace[dep_length], dep_length)
    # Smooth the end edge
    smoothedTrace[-dep_length:] = np.linspace(trace[-dep_length], trace[-1], dep_length)
    return smoothedTrace



######### Ask user input (automatic - no need to change any code here) #########
app = QApplication([])
options = QFileDialog.Options()
showInstructions("Select files.")
file_paths, _ = QFileDialog.getOpenFileNames(None, "Select files", "", "ABF Files (*.abf);;All Files (*)", options=options)

print(f"Selected files: {file_paths}")

# Ask for protocol type
protocol_types = ["Henckels", "BradleyLong", "BradleyShort"]
protocolname, ok = QInputDialog.getItem(None, "Select Protocol Type", "Enter the protocol type:", protocol_types, 0, False)

if not ok:
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Warning)
    msg.setText("No protocol type selected. Please select a protocol type.")
    msg.setWindowTitle("Warning")
    msg.exec_()
    exit()

filesnotworking = []

# Initialize summary table for recording data
columns = ['Filename', 'Peak_amplitude(pA)', 'Input_voltage(mV)', 'AreaUnderCurve(pA*mV)']
df = pd.DataFrame(columns=columns)

showInstructions("Select directory to save the concatenated table.")
save_directory = QFileDialog.getExistingDirectory(None, "Select Directory to Save Excel Files", options=options)


swpfinal = 0
for file in file_paths:
    try:
        print("\nWorking on " + file)
        abfdata = pyabf.ABF(file)
        base_filename = get_base_filename(file)  # get shortened filename
        
        # UNCOMMENT BELOW TO Plot data, with all sweeps
        #plotAllSweepsAndCommand(abfdata, base_filename, save_directory)

        swp = len(abfdata.sweepList) - 1  # analyze the last sweep
        swpfinal = swp
        abfdata.setSweep(swp)
        

        # Get start and end times of the depolarization
        startdep, enddep = getDepolarizationStartEnd(protocolname)
        startshow, endshow = getZoomStartEndTimes(protocolname)
        deptime_seconds = enddep - startdep
    
        # Extract sweep data and convert them to arrays
        time = np.array(abfdata.sweepX)
        trace = np.array(abfdata.sweepY)  # Current values
        inputv = np.array(abfdata.sweepC)
        SampleRate = abfdata.dataRate  # sample rate in total samples per second per channel
        baseline = trace[0]

        #denoise trace and remove transients
    
        filtered = low_pass_filter(trace, SampleRate)
        denoised_trace = smooth_edges(filtered, deptime_seconds, SampleRate)
        #denoised_trace= process_trace(trace, SampleRate, startdep, enddep, cutoff=300, order=5)

        # Get peak amplitude within the depolarization interval
        mask1 = (time >= startdep) & (time <= enddep)
        filtered_values = denoised_trace[mask1]  # trace values, for the depolarizing step
        filtered_time = time[mask1]

        peak_val = np.max(filtered_values)  # peak current
        index_of_peak = np.argmax(filtered_values)
        peak_loc = filtered_time[index_of_peak]

        # ## UNCOMMENT BELOW TO Plot peak pt and pulse times
        # plt.figure()
     
        # plt.plot(time, denoised_trace)
        # plt.axvline(x=startdep, color="green", linestyle='--')
        # plt.axvline(x=enddep, color="green", linestyle='--')
        # plt.plot(peak_loc, peak_val, 'o')  # show peak loc
        # plt.xlabel(abfdata.sweepLabelX)
        # plt.ylabel(abfdata.sweepLabelC)
        
        # # Add text labels to the vertical lines: y-position of the text is calculated to be vertically centered on the plot
        # plt.text(startdep, min(denoised_trace) + (max(denoised_trace) - min(denoised_trace)) * 0.5, 'Start', rotation=90, verticalalignment='center', color='green')
        # plt.text(enddep, min(denoised_trace) + (max(denoised_trace) - min(denoised_trace)) * 0.5, 'End', rotation=90, verticalalignment='center', color='green')

        # plt.title("Maximum current Induced")

        # plt.xlim(startshow, endshow) #PLOT ONLY THE REGION BETWEN STARTSHOW AND ENDSHOW
        # plt.show()

        peakamp = peak_val - baseline
        areaundercurve_dep = np.trapz(filtered_values, filtered_time)  # area under the curve
        vAtPeak = inputv[index_of_peak]  # input voltage at the time of the peak

        if peakamp is not None and areaundercurve_dep is not None and vAtPeak is not None:
            # Add filename, peakamp, areaundercurve, and voltage input to summary table
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

print(f"Mean peak amplitude(pA): {mean_a}")
print(f"Mean Input_voltage(mV): {mean_b}")
print(f"Mean area under curve(pA*mV): {mean_c}")

# Construct the file name for excel export
summary_excelname = os.path.join(save_directory, f"PeakAmplitudes_{base_filename}_sweep{swpfinal}.xlsx")

# Use ExcelWriter to save the DataFrame to an Excel file
with pd.ExcelWriter(summary_excelname, engine='xlsxwriter') as writer:
    df.to_excel(writer, sheet_name=protocolname, index=False)

# Show files not working
string = ','.join(str(x) for x in filesnotworking)
print("Files not working:" + string)


app.exit()

