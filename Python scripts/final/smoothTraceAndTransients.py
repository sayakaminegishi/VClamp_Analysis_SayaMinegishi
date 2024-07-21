''' FUNCTIONS TO SMOOTH SIGNAL AND REMOVE TRANSIENTS
Created by Sayaka (Saya) Minegishi with assistance of ChatGPT
minegishis@brandeis.edu
Jul 21 2024'''

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

############ FUNCTIONS #########################################

# Function to apply low-pass filter
def low_pass_filter(trace, SampleRate, cutoff=300, order=5):
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

def process_trace(trace, SampleRate, depStart, depEnd, cutoff=300, order=5):
    # Step 1: Smooth the edges to reduce sharp peaks
    dep_time_seconds = depEnd - depStart
    smoothed_trace = smooth_edges(trace, dep_time_seconds, SampleRate)
    
    # Step 2: Apply the low-pass filter
    filtered_trace = low_pass_filter(smoothed_trace, SampleRate, cutoff=cutoff, order=order)
    
    return filtered_trace

####### Test Script #########

# Ask user input (automatic - no need to change any code here)
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

for file in file_paths:
    try:
        abfdata = pyabf.ABF(file)
        abfdata.setSweep(5)

        # Get start and end times of the depolarization
        startdep, enddep = getDepolarizationStartEnd(protocolname)
        startshow, endshow = getZoomStartEndTimes(protocolname)

        # Extract sweep data and convert them to arrays
        time = np.array(abfdata.sweepX)
        trace = np.array(abfdata.sweepY)  # Current values
        SampleRate = abfdata.dataRate  # Sample rate in total samples per second per channel

        # Denoise trace and remove transients
       
        denoised_trace = process_trace(trace, SampleRate, startdep, enddep, cutoff=300, order=5)

        # Plot the original and filtered signals
        plt.figure(figsize=(10, 5))
        plt.plot(time, trace, label='Original Signal')
        plt.plot(time, denoised_trace, label='Denoised Signal', linestyle='--')
        plt.xlabel('Time [s]')
        plt.ylabel('Amplitude')
        plt.title(f'Processing File: {os.path.basename(file)}')
        plt.legend()
        plt.show()

    except Exception as e:
        print(f"Error processing {file}: {e}")
        filesnotworking.append(file)

# If any files failed to process, print their names
if filesnotworking:
    print("The following files could not be processed:")
    for file in filesnotworking:
        print(file)

# Exit the application
app.exit()
