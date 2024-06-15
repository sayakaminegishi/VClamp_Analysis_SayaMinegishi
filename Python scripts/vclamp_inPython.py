#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mar 24 2024

@author: sayakaminegishi

Description: main file for analyzing voltage-clamp traces.
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
import pyabf.tools.memtest

import scipy.optimize


from analyze_tail_current import analyze_tail
from createIV import create_IV

##### LOAD DATA ############
filepath = "/Users/sayakaminegishi/Documents/Birren Lab/CaCC project/DATA_Ephys/2024_06_06_01_0007.abf" #file to analyze
abfdata = pyabf.ABF(filepath)
samplerate = int(abfdata.sampleRate * 1) #sampling rate in Hz

print(abfdata) #gtives info about abfdata, such as no. of sweeps, channels, duration

###### EXAMINE DATA ############
tauVals = [] #array to store tau values for each sweep in file

for i in abfdata.sweepList:
   
    abfdata.setSweep(i)

    fig = plt.figure(figsize=(8, 5))

    # plot recorded (ADC) waveform
    axis1 = fig.add_subplot(211)
    axis1.set_title("ABF recording")
    axis1.set_ylabel(abfdata.sweepLabelY)
    axis1.set_xlabel(abfdata.sweepLabelX)
    axis1.plot(abfdata.sweepX, abfdata.sweepY, 'b', lw=.5)

    # plot command (DAC) waveform

    axis2 = fig.add_subplot(212)
    axis2.set_title("Stimulus Waveform")
    axis2.set_ylabel(abfdata.sweepLabelC)
    axis2.set_xlabel(abfdata.sweepLabelX)
    axis2.plot(abfdata.sweepX, abfdata.sweepC, 'r', lw=.5)


    plt.tight_layout()
    plt.show()


    ###### Find membrane properties across time- resistance, capacitance, holding current
    memtest = pyabf.tools.memtest.Memtest(abfdata)
    #properties in a vector, where index corresponds to time (in indices)
    holdingPotentials = memtest.Ih.values
    membraneResistances = memtest.Rm.values
    accessResistances = memtest.Ra.values
    membraneCapacitances = memtest.CmStep.values
    timeInSec = abfdata.sweepTimesMin #time in seconds

    # #take the first data pt for each property
    # RmInitial = membraneResistances(0)
    # CmInitial = membraneCapacitances(0)

    #tauVals.append(membraneResistances*membraneCapacitances) #tau time constant. TODO: CHECK IF CORRECT 
    #PLOT
    fig2 = plt.figure(figsize=(8, 5))

    #holding current
    ax1 = fig2.add_subplot(221)
    ax1.grid(alpha=.2)
    ax1.plot(abfdata.sweepTimesMin, memtest.Ih.values,
            ".", color='C0', alpha=.7, mew=0)
    ax1.set_title(memtest.Ih.name)
    ax1.set_ylabel(memtest.Ih.units)

    #membrane resistance
    ax2 = fig2.add_subplot(222)
    ax2.grid(alpha=.2)
    ax2.plot(abfdata.sweepTimesMin, memtest.Rm.values,
            ".", color='C3', alpha=.7, mew=0)
    ax2.set_title(memtest.Rm.name)
    ax2.set_ylabel(memtest.Rm.units)

    #access resistance
    ax3 = fig2.add_subplot(223)
    ax3.grid(alpha=.2)
    ax3.plot(abfdata.sweepTimesMin, memtest.Ra.values,
            ".", color='C1', alpha=.7, mew=0)
    ax3.set_title(memtest.Ra.name)
    ax3.set_ylabel(memtest.Ra.units)

    #membrane capacitance
    ax4 = fig2.add_subplot(224)
    ax4.grid(alpha=.2)
    ax4.plot(abfdata.sweepTimesMin, memtest.CmStep.values,
            ".", color='C2', alpha=.7, mew=0)
    ax4.set_title(memtest.CmStep.name)
    ax4.set_ylabel(memtest.CmStep.units)

    for ax in [ax1, ax2, ax3, ax4]:
        ax.margins(0, .9)
        ax.set_xlabel("Experiment Time (seconds)")
        for tagTime in abfdata.tagTimesMin:
            ax.axvline(tagTime, color='k', ls='--')
    plt.title("Membrane Properties for Sweep " + str(i))
    plt.tight_layout()
    plt.show()

    
    ######### EXPONENTIAL FIT FOR TAIL CURRENT #################
    #TODO: fit a model for end of vstep to trough, then trough to end of hyperpolarixation 
    #first extract the region of hyperpolarization, with hstartT & hendT as start and end of hyperpolarizing step


    x = abfdata.sweepX
    y=abfdata.sweepY

    sttime = 0.6 #start of tail current in secs
    endtime = 1.6

    analyze_tail(x,y,sttime,endtime, i, samplerate)







   



