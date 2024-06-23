'''
CREATE IV CURVE AND APPROXIMATE REVERSAL POTENTIAL FROM VOLTAGE-STEPS

This script processes ABF files to create IV curves and approximate the reversal potential.
It performs a batch-analysis on multiple selected files and calculates the mean reversal potential from all files tested.
Note: Ensure all selected files use the SAME PROTOCOL TYPE.

Created by: Sayaka (Saya) Minegishi with some help from ChatGPT.
Contact: minegishis@brandeis.edu
Date: June 23, 2024
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
from apply_low_pass_filter_FUNCTION import low_pass_filter

def find_line_of_bestFit(x1, y1, x2, y2):
    """
    Calculate the equation of a line given two points.
    (x1, y1) = first point on the line
    (x2, y2) = second point on the line
    """
    if x1 == x2:
        return None, None, x1
    
    # Calculate the slope (m)
    m = (y2 - y1) / (x2 - x1)
    
    # Calculate the y-intercept (b)
    b = y1 - m * x1
    
    return m, b, None

def createIV5(filename, protocolname):
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

    # Find the two points closest to zero current
    zero_crossings = [(i, currents[i]) for i in range(1, len(currents)) if currents[i-1] * currents[i] <= 0]

    if zero_crossings:
        i = zero_crossings[0][0]
        m, b, revVm = find_line_of_bestFit(voltages[i-1], currents[i-1], voltages[i], currents[i])
        if revVm is None:
            revVm = -b / m
        print(f"The reversal potential is approximately {revVm:.2f} mV")
    else:
        m = b = revVm = None
        print("No zero crossings found in the current data.")

    # Return a dictionary with the IV data
    iv_data = {
        "voltages": voltages,
        "currents": currents,
        "conductances": conductances,
        "reversal_potential": revVm
    }

    # Plot I/V curve
    plt.figure(figsize=(8, 5))
    plt.grid(alpha=.5, ls='--')
    plt.plot(voltages, currents, '.-', ms=15, label="I/V Data")
    plt.ylabel(abf.sweepLabelY)
    plt.xlabel("Voltage (mV)")
    plt.title(f"I/V Relationship of {abf.abfID}")

    if revVm is not None and m is not None and b is not None:
        # Plot the line of best fit
        fit_line_x = np.linspace(min(voltages), max(voltages), 100)
        fit_line_y = m * fit_line_x + b
        plt.plot(fit_line_x, fit_line_y, color="green", linestyle="--", label="Line of Best Fit")
        plt.plot(revVm, 0, 'ro', label="Reversal Potential")
        plt.legend()

    plt.show()

    # Plot Conductance vs Voltage curve
    plt.figure(figsize=(8, 5))
    plt.grid(alpha=.5, ls='--')
    plt.plot(voltages, conductances, '.-', ms=15)
    plt.ylabel("Conductance (nS)")
    plt.xlabel("Voltage (mV)")
    plt.title(f"Conductance/Voltage Relationship of {abf.abfID}")
    plt.show()

    return iv_data, revVm

####################
##### FILE SELECTION
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

iv_data_collection = [] #stores the dictionary containing IV properties from ith file. a list of dictionaries
filesnotworking = []
########### MAIN PROGRAM ###############

reversalPotentials = [] #stores the reversal potentials calculated from ith file.

for file in sorted_file_paths:
    try:
        iv_data, revVm = createIV5(file, protocolname)
        iv_data_collection.append(iv_data)
        reversalPotentials.append(revVm)
    except Exception as e:
        filesnotworking.append(file)
        logging.error(traceback.format_exc())  # log error

meanRevVm = np.average(reversalPotentials) #mean reversal potential from all the files
print(f"\nThe mean reversal potential is {meanRevVm} mV")
