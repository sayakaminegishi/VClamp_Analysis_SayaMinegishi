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



#ASK USER INPUT
filepath = "/Users/sayakaminegishi/Documents/Birren Lab/CaCC project/DATA_Ephys/2024_06_06_01_0007_BrdWN_5mMCa.abf"
abfdata = pyabf.ABF(filepath)

#tail current start and end times
starttime = 5500 #in samples
endtime = 15500 #in samples





for swp in abfdata.sweepList:

    abfdata.setSweep(swp)
    print("Number of samples per sweep: " + str(len(abfdata.sweepY))) #TODO: get uncompensated, unsubtracted channel ONLY!!!

    # Extract sweep data and convert them to arrays
    time = np.array(abfdata.sweepX)
    trace = np.array(abfdata.sweepY)  # Current values
    SampleRate = abfdata.dataRate  # sample rate in total samples per second per channel

    tailstart = time[starttime]
    tailend = time[endtime]
    # Denoise the trace
    denoised_trace = low_pass_filter(trace, SampleRate)

    # Visualize original &denoised data
    fig, axs = plt.subplots(2, sharex=True)
    fig.suptitle('Original (top) vs denoised(bottom)')
    axs[0].plot(time, trace,'tab:orange')
    axs[1].plot(time, denoised_trace, 'tab:blue')

    for ax in axs.flat:
        ax.set(xlabel='time(ms)', ylabel='current(pA)')


    plt.axvline(x = tailstart, color = 'b', label = 'tail start')
    plt.axvline(x = tailend, color = 'b', label = 'tail end')
    
 
    plt.show()

    