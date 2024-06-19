''' This program gives a visual output of a v-clamp data (in .abf format), which is selected in popup dialogue by user. 
No need for the user to change code. Just press Run.

    Created by: Sayaka (Saya) Minegishi
    Contact: minegishis@brandeis.edu
    Last modified: Jun 19 2024
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
from get_tail_times import getStartEndTail
from get_protocol_name import get_protocol_name

plt.close('all')

# Function to apply low-pass filter
def low_pass_filter(trace, SampleRate, cutoff=300, order=5):
    nyquist = 0.5 * SampleRate
    normal_cutoff = cutoff / nyquist
    b, a = scipy.signal.butter(order, normal_cutoff, btype='low', analog=False)
    filtered_trace = scipy.signal.filtfilt(b, a, trace)
    return filtered_trace


#get user input
app = QApplication([])

# Set the options for the file dialog
options = QFileDialog.Options()

# Open the file dialog and allow the user to select only one file
filepath, _ = QFileDialog.getOpenFileName(None, "Select a file", "", "ABF Files (*.abf);;All Files (*)", options=options)

# Print the selected file path
if filepath:
    print(f"Selected file: {filepath}")

protocolname = get_protocol_name()
abfdata = pyabf.ABF(filepath)
num_channels = abfdata.channelCount #number of output channels

for swp in abfdata.sweepList:

    #set channel to analyze - select only the unsubtracted
    if num_channels == 1:
        abfdata.setSweep(swp)
    else:
        abfdata.setSweep(sweepNumber= swp, channel= 1)

    #get start and end times of tail current region
    if protocolname == "Okada":
        k = swp
    else:
        k = 0 #i.e. not okada. i = sweep number for okada
    
    tailstart, tailend = getStartEndTail(protocolname, k)

    # Extract sweep data and convert them to arrays
    time = np.array(abfdata.sweepX)
    trace = np.array(abfdata.sweepY)  # Current values
    SampleRate = abfdata.dataRate  # sample rate in total samples per second per channel


    # Denoise the trace
    denoised_trace = low_pass_filter(trace, SampleRate)

    #get commandV
    abfdata.setSweep(sweepNumber= swp)
    commandv = np.array(abfdata.sweepC) 

    # Visualize denoised data & command waveform
    fig, axs = plt.subplots(2, sharex = True)
    fig.suptitle('Recorded (top) vs command (bottom)')
    axs[0].plot(time, denoised_trace,'tab:green')
    axs[1].plot(time, commandv, 'tab:red')

    axs[0].set(xlabel='time(ms)', ylabel='current(pA)')

    axs[1].set(xlabel='time(ms)', ylabel='input voltage(mV)')

   
    axs[0].axvline(x = tailstart, color = 'b', label = 'tail start', linestyle = "dashed")
    axs[0].axvline(x = tailend, color = 'b', label = 'tail end', linestyle = "dashed")


    axs[1].axvline(x = tailstart, color = 'b', label = 'tail start', linestyle = "dashed")
    axs[1].axvline(x = tailend, color = 'b', label = 'tail end', linestyle = "dashed")
   
    plt.show()

    