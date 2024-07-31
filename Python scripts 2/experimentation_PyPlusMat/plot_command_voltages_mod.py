#plot_command_voltages_mod.py
import pyabf
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib import gridspec
import scipy
from scipy import signal
from scipy.signal import find_peaks
from scipy.optimize import curve_fit

def plot_command_V(filepath):
    abfdata = pyabf.ABF(filepath)
    print(abfdata) #gtives info about abfdata, such as no. of sweeps, channels, duration
    print(abfdata.sweepC)
    
    for i in abfdata.sweepList:
        abfdata.setSweep(i)
        plt.plot(abfdata.sweepX, abfdata.sweepC, alpha=.5, label="sweep %d" % (i))
        plt.legend()
    
         plt.show()
    