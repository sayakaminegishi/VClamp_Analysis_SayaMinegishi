#testing functions

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
#####################################################

######### DEFINE NECESSARY FUNCTIONS ###########################
def low_pass_filter(trace, SampleRate, cutoff=300, order=5):
    nyquist = 0.5 * SampleRate
    normal_cutoff = cutoff / nyquist
    b, a = scipy.signal.butter(order, normal_cutoff, btype='low', analog=False)
    filtered_trace = scipy.signal.filtfilt(b, a, trace)
    return filtered_trace


####################################
file = "/Users/sayakaminegishi/Documents/Birren Lab/CaCC project/DATA_Ephys/7_3_2024_recordings/toANALYZE_BRADLEYS/2024_07_03_01_0011.abf"
protocolname = 'BradleyShort'


abfdata = pyabf.ABF(file)
abfdata.setSweep(10)

time = np.array(abfdata.sweepX)
trace = np.array(abfdata.sweepY)
inputv = np.array(abfdata.sweepC)
SampleRate = abfdata.dataRate

denoised_trace = low_pass_filter(trace, SampleRate)


# Get peak current amplitude during depolarization step
starttime, endtime = getDepolarizationStartEnd(protocolname)
#index of starttime in denoised_trace
startmask = denoised_trace.index(min(abs(starttime-time))) #1 for the index of the closest point to starttime
baseline = np.average(denoised_trace[0:startmask-1]) #baseline is the average of all pts before depolarization begins

print(baseline)
