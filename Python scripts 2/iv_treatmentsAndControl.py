'''
CREATE IV CURVE FOR CONTROL AND TREATMENT FILE(S) AND PLOTS THEM ON THE SAME AXES.
Does not take average or fit a curve.

This script processes ABF files to create an IV curve for each file

Note: Ensure all selected files use the SAME PROTOCOL TYPE.

Created by: Sayaka (Saya) Minegishi with some help from ChatGPT.
Contact: minegishis@brandeis.edu
Date: July 4, 2024
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
from PyQt5.QtWidgets import QApplication, QFileDialog, QInputDialog, QMessageBox, QWidget
from getFilePath import get_file_path  # type: ignore
from get_tail_times import getStartEndTail, getDepolarizationStartEnd, get_last_sweep_number
from remove_abf_extension import remove_abf_extension  # type: ignore
from getTailCurrentModel import getExpTailModel
from getFilePath import get_only_filename
from apply_low_pass_filter_FUNCTION import low_pass_filter


def showInstructions(messagetoshow):
    # Show given message as a dialog box
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Information)
    msg.setText(messagetoshow)
    msg.setWindowTitle("Information")
    msg.setStandardButtons(QMessageBox.Ok)
    msg.exec_()


def IV_nolineofbestfit(filename, protocolname):
    # filename = path to file
    abf = pyabf.ABF(filename)
    SampleRate = abf.dataRate

    # Loop through sweeps and process each one
    currents = []
    voltages = []
    conductances = []
    
    for sweep in abf.sweepList:
        abf.setSweep(sweep)
        
        # Extract raw sweep data
        time = np.array(abf.sweepX)
        trace = np.array(abf.sweepY)

        # Denoise the trace
        denoised_trace = low_pass_filter(trace, SampleRate) #low_pass_filter can only accept 1D data, which is trace, NOT an abf object

        # Start and end times of voltage steps, in seconds
        st, en = getDepolarizationStartEnd(protocolname)

        # Convert these to indices
        stindx = np.argmin(np.abs(time - st))  # Closest index to start time
        enidx = np.argmin(np.abs(time - en))   # Closest index to end time

        # Extract current and voltage at the end index
        curr = denoised_trace[enidx-3]  # Current for the depolarizing step
        volt = abf.sweepC[enidx-3]  # Voltage for the depolarizing step
        conduc = curr / volt if volt != 0 else np.nan  # Conductance for the depolarizing step, avoid division by zero

        # Store the data
        currents.append(curr)
        voltages.append(volt)
        conductances.append(conduc)

    # Return a dictionary with the IV data
    iv_data = {
        "voltages": voltages,
        "currents": currents,
        "conductances": conductances,
    }
    
    return iv_data

####################
##### FILE SELECTION
# Main script
app = QApplication([])

# Select control files
showInstructions("Select control files")
options = QFileDialog.Options()

file_paths_control, _ = QFileDialog.getOpenFileNames(None, "Select control files", "", "ABF Files (*.abf);;All Files (*)", options=options)

if not file_paths_control:
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Warning)
    msg.setText("No file selected. Please select a file.")
    msg.setWindowTitle("Warning")
    msg.exec_()
    exit()

sorted_file_paths_control = sorted(file_paths_control)

# Select treatment files (eg blocker)
showInstructions("Select treatment files")
options = QFileDialog.Options()
file_paths_treat, _ = QFileDialog.getOpenFileNames(None, "Select treatment files", "", "ABF Files (*.abf);;All Files (*)", options=options)

if not file_paths_treat:
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Warning)
    msg.setText("No file selected. Please select a file.")
    msg.setWindowTitle("Warning")
    msg.exec_()
    exit()
sorted_file_paths_treat = sorted(file_paths_treat)

# Select directory to save Excel files
showInstructions("Select directory to save summary files")
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

iv_data_collection_control = [] #stores the dictionary containing IV properties from ith file. a list of dictionaries
iv_data_collection_treat = [] #stores the dictionary containing IV properties from ith file. a list of dictionaries
filesnotworking = []

########### MAIN PROGRAM ###############

# Control files
for file in sorted_file_paths_control:
    try:
        iv_data = IV_nolineofbestfit(file, protocolname)
        iv_data_collection_control.append(iv_data)
    except Exception as e:
        filesnotworking.append(file)
        logging.error(traceback.format_exc())  # log error

# Treatment files
for file in sorted_file_paths_treat:
    try:
        iv_data = IV_nolineofbestfit(file, protocolname)
        iv_data_collection_treat.append(iv_data)
    except Exception as e:
        filesnotworking.append(file)
        logging.error(traceback.format_exc())  # log error

# Plot I/V curve
plt.figure(figsize=(12, 6))

# Control data plotting
for iv_data in iv_data_collection_control:
    plt.plot(iv_data["voltages"], iv_data["currents"], marker='o', linestyle='-', label='Control')

# Treatment data plotting
for iv_data in iv_data_collection_treat:
    plt.plot(iv_data["voltages"], iv_data["currents"], marker='x', linestyle='--', label='Treatment')

plt.title("I/V Relationship (Control vs. Treatment)")
plt.xlabel("Voltage (mV)")
plt.ylabel("Current (pA)")
plt.legend()
plt.grid(alpha=0.5, linestyle='--')
plt.tight_layout()

# Display the plot
plt.show()

# Show completion message as a dialog box
msg = QMessageBox()
msg.setIcon(QMessageBox.Information)
msg.setText("Program complete")
msg.setWindowTitle("Information")
msg.setStandardButtons(QMessageBox.Ok)
msg.exec_()
