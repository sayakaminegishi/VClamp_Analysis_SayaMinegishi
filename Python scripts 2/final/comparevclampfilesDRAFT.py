import os
import numpy as np
import scipy.optimize
import scipy.signal
import matplotlib.pyplot as plt
import pyabf
import pandas as pd
import traceback
import logging
from PyQt5.QtWidgets import QApplication, QFileDialog, QInputDialog, QMessageBox
from getFilePath import get_file_path  # type: ignore
from get_tail_times import getStartEndTail, getDepolarizationStartEnd, get_last_sweep_number
from remove_abf_extension import remove_abf_extension  # type: ignore
from getTailCurrentModel import getExpTailModel
from getFilePath import get_only_filename
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QInputDialog
from datetime import datetime

# Function to extract timestamp from file name
def extract_timestamp(file_name):
    return datetime.strptime(file_name[-13:-4], "%Y%m%d%H")

######### Define necessary functions
def showInstructions(messagetoshow):
    # Show given message as a dialog box
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Information)
    msg.setText(messagetoshow)
    msg.setWindowTitle("Information")
    msg.setStandardButtons(QMessageBox.Ok)
    msg.exec_()

def low_pass_filter(trace, SampleRate, cutoff=300, order=5):
    nyquist = 0.5 * SampleRate
    normal_cutoff = cutoff / nyquist
    b, a = scipy.signal.butter(order, normal_cutoff, btype='low', analog=False)
    filtered_trace = scipy.signal.filtfilt(b, a, trace)
    return filtered_trace
###################################

# Main script
app = QApplication([])

# Select files
showInstructions("Select files to analyze")
options = QFileDialog.Options()
file_paths, _ = QFileDialog.getOpenFileNames(None, "Select files", "", "ABF Files (*.abf);;All Files (*)", options=options)

if not file_paths:
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Warning)
    msg.setText("No file selected. Please select a file.")
    msg.setWindowTitle("Warning")
    msg.exec_()
    exit()

sorted_file_paths = sorted(file_paths)

# Select directory to save Excel files
showInstructions("Select directory to save results")
save_directory = QFileDialog.getExistingDirectory(None, "Select Directory to Save Excel Files", options=options)

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

# Ask for sweep number
sweepn, ok = QInputDialog.getText(None, "Enter Sweep Number", "Enter the sweep number to analyze, or enter 'final' for the last sweep:")

if not ok:
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Warning)
    msg.setText("No sweep number entered. Please enter a sweep number.")
    msg.setWindowTitle("Warning")
    msg.exec_()
    exit()

if sweepn == "final":
    sweepnumber = int(get_last_sweep_number(protocolname))
else:
    sweepnumber = int(sweepn)-1

# Add a dialogue box for user to specify the last 4 digits of the files that mark blocker start and blocker end times
# Ask the user for the last 4 digits of the start file
window = QWidget()
start_file_digits, ok1 = QInputDialog.getText(window, 'Input', 'Enter the last 4 digits of the file that marks the blocker start time:')
if not ok1 or not start_file_digits:
    print("Start file digits were not provided.")
    exit()

# Ask the user for the last 4 digits of the end file
end_file_digits, ok2 = QInputDialog.getText(window, 'Input', 'Enter the last 4 digits of the file that marks the blocker end time:')
if not ok2 or not end_file_digits:
    print("End file digits were not provided.")
    exit()

# Combine the digits with an underscore
startblock = "_" + start_file_digits
endblock = "_" + end_file_digits

if startblock and endblock:
    print(f"Start file: {startblock}")
    print(f"End file: {endblock}")

# Create array to save files not working
filesnotworking = []

# Initialize summary table for recording data
columns = ['Filename', 'Peak_amplitude(pA)', 'current_at_peak(pA)', 'Input_voltage_at_peak(mV)', 'AreaUnderCurve_peak(pA*mV)']

df = pd.DataFrame(columns=columns)

# Create arrays for storing properties for each file
max_amplitudes = []
max_tail_amplitudes = []
area_under_curves_tail = []
tau_vals_tail = []
areasundercurve_peak = []
file_names_list = []
time_differences = []

# Get the timestamp of the first file
first_file_timestamp = extract_timestamp(get_only_filename(sorted_file_paths[0]))

for file in sorted_file_paths:
    try:
        file_shortname = get_only_filename(file)
        filen_lastdig = file_shortname[-9:-4]

        # Calculate the time difference from the first file
        current_file_timestamp = extract_timestamp(file_shortname)
        time_diff = (current_file_timestamp - first_file_timestamp).total_seconds()
        time_differences.append(time_diff)

        print(f"\nWorking on {file_shortname}\n")

        abfdata = pyabf.ABF(file)
        abfdata.setSweep(sweepnumber)

        time = np.array(abfdata.sweepX)
        trace = np.array(abfdata.sweepY)
        inputv = np.array(abfdata.sweepC)
        SampleRate = abfdata.dataRate
        #baseline = trace[0] 

        denoised_trace = low_pass_filter(trace, SampleRate)

        # Get peak current amplitude during depolarization step
        starttime, endtime = getDepolarizationStartEnd(protocolname)

        # Calculate baseline as the average current from 0 to starttime
        startmask = np.argmin(np.abs(time - starttime)) #get CLOSEST INDEX to starttime
        baseline = np.average(denoised_trace[:startmask])

        mask2 = (time >= starttime) & (time <= endtime)
        if not np.any(mask2):
            raise ValueError("No data points found in the specified depolarization region.")

        filtered_values2 = denoised_trace[mask2]  # Depolarized region, y
        filtered_time2 = time[mask2]  # Depolarized region, x
        inputv2 = inputv[mask2]

        # Calculate the start index for the last 0.0012 seconds
        duration = endtime - starttime
        last_duration = 0.0012
        if duration < last_duration:
            raise ValueError("The depolarization period is shorter than 0.0012 seconds.")

        start_index = np.searchsorted(filtered_time2, endtime - last_duration)
        if start_index == len(filtered_time2):
            raise ValueError("The calculated start index for the last 0.0012 seconds is out of range.")

        # Average of y-values in the last 0.0012 seconds
        last_values = filtered_values2[start_index:]
        peak_val = np.mean(last_values)

        # Peak location (use the index from filtered_time2)
        index_of_pk = np.argmax(filtered_values2) #changed Jul8
        peak_loc = filtered_time2[index_of_pk]

        peak_amp = peak_val - baseline
        areaundercurve_peak = np.trapz(filtered_values2, filtered_time2)
        vAtPeak = inputv2[index_of_pk]
        currpeak = peak_val

        # Printing values for debugging
        print(f"Peak Value: {peak_val}")
        print(f"Peak Location: {peak_loc}")
        print(f"Peak Amplitude: {peak_amp}")
        print(f"Area Under Curve: {areaundercurve_peak}")
        print(f"Voltage at Peak: {vAtPeak}")

        # Add properties to the summary table
        new_row = {
            'Filename': file_shortname,
            'Peak_amplitude(pA)': peak_amp,
            'current_at_peak(pA)': currpeak,
            'Input_voltage_at_peak(mV)': vAtPeak,
            'AreaUnderCurve_peak(pA*mV)': areaundercurve_peak,
        }

        max_amplitudes.append(peak_amp)
        areasundercurve_peak.append(areaundercurve_peak)
        file_names_list.append(filen_lastdig)

        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

    except Exception as e:
        filesnotworking.append(file)
        logging.error(traceback.format_exc())  # log error

###########################################################
# Get summary data
print(df)

# Plot each feature and compare across files
fig, axs = plt.subplots(2, 1, figsize=(12, 8))

# Plot peak amplitude
axs[0].plot(time_differences, max_amplitudes, 'o-')
axs[0].set_title('Peak Amplitude Over Time')
axs[0].set_xlabel('Time (s)')
axs[0].set_ylabel('Peak Amplitude (pA)')

# Plot area under curve at peak
axs[1].plot(time_differences, areasundercurve_peak, 'o-')
axs[1].set_title('Area Under Curve at Peak Over Time')
axs[1].set_xlabel('Time (s)')
axs[1].set_ylabel('Area Under Curve (pA*mV)')

# Add blocker start and end times as vertical lines
start_time_diff = (extract_timestamp(startblock) - first_file_timestamp).total_seconds()
end_time_diff = (extract_timestamp(endblock) - first_file_timestamp).total_seconds()

axs[0].axvline(x=start_time_diff, color='r', linestyle='--', linewidth=2)
axs[0].axvline(x=end_time_diff, color='r', linestyle='--', linewidth=2)
axs[1].axvline(x=start_time_diff, color='r', linestyle='--', linewidth=2)
axs[1].axvline(x=end_time_diff, color='r', linestyle='--', linewidth=2)

plt.tight_layout()
plt.show()

###############################

# Export all the dataframes from all the files analyzed to a single Excel file
summary_excelname = os.path.join(save_directory, f"VclampSummary_{protocolname}_sweep{sweepnumber}_NOTAIL.xlsx")

# Use ExcelWriter to save the DataFrame to an Excel file
with pd.ExcelWriter(summary_excelname, engine='xlsxwriter') as writer:
    df.to_excel(writer, sheet_name=protocolname, index=False)

# Show files not working
string = ', '.join(str(x) for x in filesnotworking)
print(f"Files not working: {string}")
