import numpy as np
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
from smoothTraceAndTransients import low_pass_filter, smooth_edges, process_trace

######### Ask user input (automatic - no need to change any code here) #########
app = QApplication([])
options = QFileDialog.Options()
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
save_directory = QFileDialog.getExistingDirectory(None, "Select Directory to Save Excel Files", options=options)

swpfinal = 0
for file in file_paths:
    try:
        print("\nWorking on " + file)
        abfdata = pyabf.ABF(file)
        base_filename = get_base_filename(file)  # Get shortened filename
        
        # Plot data, with all sweeps
        plotAllSweepsAndCommand(abfdata, base_filename, save_directory)

        swp = len(abfdata.sweepList) - 1  # Analyze the last sweep
        swpfinal = swp
        abfdata.setSweep(swp)
        
        # Get start and end times of the depolarization
        startdep, enddep = getDepolarizationStartEnd(protocolname)
        startshow, endshow = getZoomStartEndTimes(protocolname)
    
        # Extract sweep data and convert them to arrays
        time = np.array(abfdata.sweepX)
        trace = np.array(abfdata.sweepY)  # Current values
        inputv = np.array(abfdata.sweepC)
        SampleRate = abfdata.dataRate  # Sample rate in total samples per second per channel
        baseline = trace[0]

        # Denoise trace and remove transients
        denoised_trace = process_trace(trace, SampleRate, startdep, enddep, cutoff=300, order=5)

        # Get peak amplitude within the depolarization interval
        mask1 = (time >= startdep) & (time <= enddep)
        filtered_values = denoised_trace[mask1]  # Trace values, for the depolarizing step
        filtered_time = time[mask1]

        peak_val = np.max(filtered_values)  # Peak current
        index_of_peak = np.argmax(filtered_values)
        peak_loc = filtered_time[index_of_peak]

        # Plot peak pt and pulse times
        plt.figure()
        plt.plot(time, denoised_trace)
        plt.axvline(x=startdep, color="green", linestyle='--')
        plt.axvline(x=enddep, color="green", linestyle='--')
        plt.plot(peak_loc, peak_val, 'o')  # Show peak location
        plt.xlabel(abfdata.sweepLabelX)
        plt.ylabel(abfdata.sweepLabelC)

        # Add text labels to the vertical lines
        plt.text(startdep, min(denoised_trace) + (max(denoised_trace) - min(denoised_trace)) * 0.5, 'Start', rotation=90, verticalalignment='center', color='green')
        plt.text(enddep, min(denoised_trace) + (max(denoised_trace) - min(denoised_trace)) * 0.5, 'End', rotation=90, verticalalignment='center', color='green')

        plt.title("Maximum current Induced")
        plt.xlim(startshow, endshow)  # Plot only the region between startshow and endshow
        plt.show()

        # Compute peak amplitude and area under the curve
        peakamp = peak_val - baseline
        areaundercurve_dep = np.trapz(filtered_values, filtered_time)  # Area under the curve
        vAtPeak = inputv[index_of_peak]  # Input voltage at the time of the peak

        if peakamp is not None and areaundercurve_dep is not None and vAtPeak is not None:
            # Add filename, peakamp, areaundercurve, and voltage input to summary table
            new_row = {'Filename': file, 'Peak_amplitude(pA)': peakamp, 'Input_voltage(mV)': vAtPeak, 'AreaUnderCurve(pA*mV)': areaundercurve_dep}
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    except Exception as e:
        filesnotworking.append(file)
        logging.error(traceback.format_exc())  # Log error

# Get summary data for the cell
print(df)  # Show the recorded data

print("\nMean of each column:")

mean_a = df['Peak_amplitude(pA)'].mean()
mean_b = df['Input_voltage(mV)'].mean()
mean_c = df['AreaUnderCurve(pA*mV)'].mean()

print(f"Mean peak amplitude(pA): {mean_a}")
print(f"Mean Input_voltage(mV): {mean_b}")
print(f"Mean area under curve(pA*mV): {mean_c}")

# Construct the file name for excel export
summary_excelname = os.path.join(save_directory, f"PeakAmplitudes_{protocolname}_sweep{swpfinal}.xlsx")

# Use ExcelWriter to save the DataFrame to an Excel file
with pd.ExcelWriter(summary_excelname, engine='xlsxwriter') as writer:
    df.to_excel(writer, sheet_name=protocolname, index=False)

# Show files not working
string = ','.join(str(x) for x in filesnotworking)
print("Files not working:" + string)
