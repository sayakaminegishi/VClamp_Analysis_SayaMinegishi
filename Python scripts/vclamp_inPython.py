#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mar 24 2024

@author: sayakaminegishi

Description: main file for analyzing voltage-clamp traces. sweep numbers use 0-based indexing (eg to get 1st sweep, enter 0).
"""
#TODO: fix memtest

import os
import numpy as np
import scipy.optimize
import scipy.signal
import matplotlib.pyplot as plt
import pyabf
import pandas as pd
import traceback
import logging
from PyQt5.QtWidgets import QApplication, QFileDialog
from getFilePath import get_file_path # type: ignore
from get_tail_times import getStartEndTail
from remove_abf_extension import remove_abf_extension # type: ignore
from getTailCurrentModel import getExpTailModel
import pyabf.tools.memtest

##### LOAD DATA ############
app = QApplication([])

# Options for the file dialog
options = QFileDialog.Options()

# Ask user to select a single file
filepath, _ = QFileDialog.getOpenFileName(None, "Select a file", "", "ABF Files (*.abf);;All Files (*)", options=options)

if not filepath:
    print("No file selected. Exiting...")
    exit()

print(f"Selected file: {filepath}")

# Ask user to select a directory to save the Excel file
save_directory = QFileDialog.getExistingDirectory(None, "Select Directory to Save Excel File", options=options)

if not save_directory:
    print("No directory selected. Exiting...")
    exit()

print(f"Selected save directory: {save_directory}")


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

    timeInSec = abfdata.sweepTimesMin #time in seconds
    memtest = pyabf.tools.memtest.Memtest(abfdata)
    #properties in a vector, where index corresponds to time (in indices)
    holdingPotentials = memtest.Ih.values
    membraneResistances = memtest.Rm.values
    accessResistances = memtest.Ra.values
    membraneCapacitances = memtest.CmStep.values


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


    #calculate conductance
    #g = I/V
    conductance = (np.array(abfdata.sweepY))/(np.array(abfdata.sweepC))

    print(str(conductance))


    


#     ######### EXPONENTIAL FIT FOR TAIL CURRENT #################



   



