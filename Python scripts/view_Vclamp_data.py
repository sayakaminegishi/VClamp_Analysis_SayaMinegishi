''' This program gives a visual output of a selected v-clamp data (in .abf format). 

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

plt.close('all')

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
protocolname = "BradleyLong"
i = 0 #i.e. not okada. i = sweep number for okada
tailstart, tailend = getStartEndTail(protocolname, i)





for swp in abfdata.sweepList:

    abfdata.setSweep(sweepNumber= swp, channel= 1) #channel = 1 shows unsubtracted trace
    #TODO: make if/else so that if numChannels<2, channel is always 0
    
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

    