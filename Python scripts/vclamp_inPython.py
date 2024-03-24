#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mar 24 2024

@author: sayakaminegishi
"""
#pip install pyabf
# pip install IPFX
import pyabf
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib import gridspec
import scipy
from scipy import signal
from scipy.signal import find_peaks
from scipy.optimize import curve_fit


#load data
filepath = "/Users/sayakaminegishi/Documents/Birren Lab/Voltage clamp analysis/voltage clamp example data/2016_05_19_07_0002 (1).abf"
abfdata = pyabf.ABF(filepath)
print(abfdata) #gtives info about abfdata, such as no. of sweeps, channels, duration



fig = plt.figure(figsize=(8, 5))

# plot recorded (ADC) waveform
plt.subplot(211)
plt.plot(abfdata.sweepX, abfdata.sweepY)
plt.xlabel(abfdata.sweepLabelX)
plt.ylabel(abfdata.sweepLabelY)

# plot command (DAC) waveform
plt.subplot(212)
plt.plot(abfdata.sweepX, abfdata.sweepC, 'r')
plt.xlabel(abfdata.sweepLabelX)
plt.ylabel(abfdata.sweepLabelC)

plt.tight_layout()
plt.show()

print(abfdata.sweepC)


