#calculate conductance of ion channel

import pyabf
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib import gridspec
import scipy
from scipy import signal
from scipy.signal import find_peaks
from scipy.optimize import curve_fit
import pyabf.tools.memtest

import scipy.optimize
##### LOAD DATA ############
filepath = "/Users/sayakaminegishi/Documents/Birren Lab/CaCC project/DATA_Ephys/2024_06_06_01_0005.abf" #file to analyze
abfdata = pyabf.ABF(filepath)
samplerate = int(abfdata.sampleRate * 1) #sampling rate in Hz
##########################
#set last sweep
lastsw = len(abfdata.sweepList)-1

abfdata.setSweep(lastsw)
current = np.array(abfdata.sweepY)
voltage = np.array(abfdata.sweepC)
time = np.array(abfdata.sweepX)

from createIV import createIV
createIV(filepath)

# conductance=current/voltage #conductance values, in an array, for this sweep

# # Show conductance
# string = ','.join(str(x) for x in conductance)
# print("Conductance values:" + string)

# print(np.size(conductance)) 

# print("max conductance is" + str(max(conductance)) + "nanosiemens")

# plt.figure()
# plt.plot(voltage, conductance)
# plt.show()
# #TODO: get conductance at reversal potential