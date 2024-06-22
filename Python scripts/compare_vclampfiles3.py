''' COMPARES CURRENT PROPERTIES BETWEEN FILES, WITH A GIVEN SWEEP NUMBER AND PROTOCOL.

Created by: Sayaka (Saya) Minegishi, with some support from chatgpt.
Contact: minegishis@brandeis.edu
Last modified: June 22 2024

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
from PyQt5.QtWidgets import QApplication, QFileDialog, QInputDialog, QMessageBox
from getFilePath import get_file_path  # type: ignore
from get_tail_times import getStartEndTail, getDepolarizationStartEnd, get_last_sweep_number
from remove_abf_extension import remove_abf_extension  # type: ignore
from getTailCurrentModel import getExpTailModel
from getFilePath import get_only_filename


def low_pass_filter(trace, SampleRate, cutoff=300, order=5):
    nyquist = 0.5 * SampleRate
    normal_cutoff = cutoff / nyquist
    b, a = scipy.signal.butter(order, normal_cutoff, btype='low', analog=False)
    filtered_trace = scipy.signal.filtfilt(b, a, trace)
    return filtered_trace

def monoExp(x, a, b, c):
    return a * np.exp(b * x) + c

def analyze_tail(time, trace, trough, HypEnd, SampleRate):
    mask = (time >= trough) & (time <= HypEnd)  # region to analyze - from trough to end of tail

    if not np.any(mask):
        print("Error: No data points found in the specified tail region.")
        return None, None, None, None

    # Fit exponential model to part of tail after trough with initial guess and bounds
    initial_guess = [1, -1, 1]
    bounds = ([-np.inf, -np.inf, -np.inf], [np.inf, 0, np.inf])  # b should be negative for decay

    try:
        params, cv = scipy.optimize.curve_fit(monoExp, time[mask], trace[mask], p0=initial_guess, bounds=bounds, maxfev=10000)
        a, b, c = params
        tauSec = -1 / b  # Tau (time constant)

        # Determine quality of the fit
        squaredDiffs = np.square(trace[mask] - monoExp(time[mask], *params))
        squaredDiffsFromMean = np.square(trace[mask] - np.mean(trace[mask]))
        rSquared = 1 - np.sum(squaredDiffs) / np.sum(squaredDiffsFromMean)
        print(f"R² = {rSquared}")
        print(f"Y = {a} * exp({b} * x) + {c}")
        print(f"Tau = {tauSec} sec")

        # Visualize fitted curve
        plt.scatter(time, trace, label="data")
        x_fit = np.linspace(time[mask].min(), time[mask].max(), 1000)  # x values for line of best fit
        y_fit = monoExp(x_fit, *params)  # y values for fitted curve
        plt.plot(x_fit, y_fit, c="red", label="fit")
        plt.legend()
        plt.show()

        return a, b, c, tauSec, rSquared

    except RuntimeError as e:
        print(f"Error: {e}")
        return None, None, None, None

def get_tail_model(afound, bfound, cfound):
    try:
       
        if afound is not None and bfound is not None and cfound is not None:
            # Print the averaged line of best fit
            print(f"Averaged line of best fit: y = {afound:.3e} * exp({bfound:.2f} * x) + {cfound:.2f}")

            # Return resulting curve
            x_values = np.linspace(trough_loc, endtime, 1000)
            y_values = monoExp(x_values, afound, bfound, cfound)
            return x_values, y_values

    except Exception as e:
        logging.error(traceback.format_exc())  # log error

    return None, None

# Main script
app = QApplication([])

# Select files
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
sweepn, ok = QInputDialog.getText(None, "Enter Sweep Number", "Enter the sweep number to analyze (zero-indexed), or enter 'final' for the last sweep:")

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
    sweepnumber = int(sweepn)

# Create array to save files not working
filesnotworking = []

# Initialize summary table for recording data
columns = ['Filename', 'Peak_amplitude(pA)', 'Input_voltage_at_peak(mV)', 'AreaUnderCurve_peak(pA*mV)',
           'Tail_amplitude(pA)', 'Input_voltage_at_trough(mV)', 'AreaUnderCurve_tail(pA*mV)', 'Tau(sec)']

df = pd.DataFrame(columns=columns)

# Create arrays for storing properties for each file
max_amplitudes = []
max_tail_amplitudes = []
area_under_curves_tail = []
tau_vals_tail = []
areasundercurve_peak = []
file_names_list = []

for file in sorted_file_paths:
    try:
        file_shortname = get_only_filename(file)
        filen_lastdig = file_shortname[-9:-4]

        print(f"\nWorking on {file_shortname}\n")
        

        abfdata = pyabf.ABF(file)
        abfdata.setSweep(sweepnumber)

        time = np.array(abfdata.sweepX)
        trace = np.array(abfdata.sweepY)
        inputv = np.array(abfdata.sweepC)
        SampleRate = abfdata.dataRate
        baseline = trace[0]

        denoised_trace = low_pass_filter(trace, SampleRate)

        # Get tail amplitude
        startTail, endTail = getStartEndTail(protocolname, sweepnumber)

        mask1 = (time >= startTail) & (time <= endTail)
        if not np.any(mask1):
            raise ValueError("No data points found in the specified tail region.")
        
        filtered_values = denoised_trace[mask1]
        filtered_time = time[mask1]
        inputv1 = inputv[mask1]

        trough_val = np.min(filtered_values)
        index_of_trough = np.argmin(filtered_values)
        trough_loc = filtered_time[index_of_trough] #+ startTail

        trough_amp = trough_val - baseline
        areaundercurve_tail = np.trapz(filtered_values, filtered_time)
        vAtTrough = inputv1[index_of_trough]

        # Get peak current amplitude during depolarization step
        starttime, endtime = getDepolarizationStartEnd(protocolname)
        mask2 = (time >= starttime) & (time <= endtime)
        if not np.any(mask2):
            raise ValueError("No data points found in the specified depolarization region.")
        
        filtered_values2 = denoised_trace[mask2]
        filtered_time2 = time[mask2]
        inputv2 = inputv[mask2]

        peak_val = np.min(filtered_values2)
        index_of_pk = np.argmin(filtered_values2)
        peak_loc = filtered_time2[index_of_pk] #+ starttime

        peak_amp = peak_val - baseline
        areaundercurve_peak = np.trapz(filtered_values2, filtered_time2)
        vAtPeak = inputv2[index_of_pk]

        # Fit exponential model to tail current & get tau and R²
        a, b, c, tauSec, rSquared = analyze_tail(time, trace, trough_loc, endTail, SampleRate)
        if a is None or b is None or c is None or tauSec is None:
            raise ValueError("Exponential fit to tail current failed.")
        
        xtail, ytail= get_tail_model(a,b,c) 

        plt.figure(figsize=(10, 6))
        plt.plot(xtail, ytail, label=f"y = {a:.2f} * exp({b:.2f} * x) + {c:.2f}", color='red')
        plt.xlabel('Time (s)')
        plt.ylabel('Current (pA)')
        plt.title(f'Averaged curve of Best Fit for Sweep {sweepnumber}, {file_shortname}')
        plt.legend()
        plt.grid(True)
        plt.show()

        # Add properties to the summary table
        new_row = {
            'Filename': file_shortname,
            'Peak_amplitude(pA)': peak_amp,
            'Input_voltage_at_peak(mV)': vAtPeak,
            'AreaUnderCurve_peak(pA*mV)': areaundercurve_peak,
            'Tail_amplitude(pA)': trough_amp,
            'Input_voltage_at_trough(mV)': vAtTrough,
            'AreaUnderCurve_tail(pA*mV)': areaundercurve_tail,
            'Tau(sec)': tauSec
        }

        max_amplitudes.append(peak_amp)
        max_tail_amplitudes.append(trough_amp)
        area_under_curves_tail.append(areaundercurve_tail)
        areasundercurve_peak.append(areaundercurve_peak)
        tau_vals_tail.append(tauSec)
        file_names_list.append(filen_lastdig)

        
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

    except Exception as e:
        filesnotworking.append(file)
        logging.error(traceback.format_exc())  # log error
###########################################################
# Get summary data
print(df)


#plot each feature and compare across files
fig, axs = plt.subplots(3,2,figsize = (12,10))

#first subplot - max_amplitudes (peak amplitude during V-step)
axs[0, 0].plot(file_names_list, max_amplitudes, marker='o')
axs[0, 0].set_title(f"Maximum current amplitude for each file, sweep {sweepnumber}")
axs[0, 0].set_xlabel('File name')
axs[0, 0].set_ylabel('current amplitude (pA)')
axs[0, 0].tick_params(axis='x', rotation=45)  # Rotate x-axis labels


#second subplot - max_tail_amplitudes
axs[0, 1].plot(file_names_list, max_tail_amplitudes, marker='o', color='orange')
axs[0, 1].set_title(f"Tail current amplitudes, sweep {sweepnumber}")
axs[0, 1].set_xlabel('File name')
axs[0, 1].set_ylabel('Tail current amplitude (pA)')
axs[0, 1].tick_params(axis='x', rotation=45)  # Rotate x-axis labels
axs[0, 1].tick_params(axis='x', rotation=45)  # Rotate x-axis labels

#third subplot - max_tail_amplitudes
axs[1, 0].plot(file_names_list, area_under_curves_tail, marker='o', color='green')
axs[1, 0].set_title(f"Area under curve for tail current, sweep {sweepnumber}")
axs[1, 0].set_xlabel('File name')
axs[1, 0].set_ylabel('Area(pA*s)')
axs[1, 0].tick_params(axis='x', rotation=45)  # Rotate x-axis labels


#fourth subplot
axs[1, 1].plot(file_names_list, areasundercurve_peak, marker='o', color='purple')
axs[1, 1].set_title(f"Area under curve at the end of voltage-step, sweep {sweepnumber}")
axs[1, 1].set_xlabel('File name')
axs[1, 1].set_ylabel('Area(pA*s)')
axs[1, 1].tick_params(axis='x', rotation=45)  # Rotate x-axis labels


#fifth subplot - tau_vals_tail
axs[2, 0].plot(file_names_list, tau_vals_tail, marker='o', color = 'cyan')
axs[2, 0].set_title(f"Tau values (s), sweep {sweepnumber}")
axs[2, 0].set_xlabel('File name')
axs[2, 0].set_ylabel('Tau(s)')
axs[2, 0].tick_params(axis='x', rotation=45)  # Rotate x-axis labels

# Hide the empty subplot (bottom-right)
fig.delaxes(axs[2, 1])

# Adjust layout to prevent overlap
plt.tight_layout()

# Display the plot
plt.show()





###############################

# Export all the dataframes from all the files analyzed to a single Excel file
summary_excelname = os.path.join(save_directory, f"VclampSummary_{protocolname}_sweep{sweepnumber}.xlsx")

# Use ExcelWriter to save the DataFrame to an Excel file
with pd.ExcelWriter(summary_excelname, engine='xlsxwriter') as writer:
    df.to_excel(writer, sheet_name=protocolname, index=False)

# Show files not working
string = ', '.join(str(x) for x in filesnotworking)
print(f"Files not working: {string}")
