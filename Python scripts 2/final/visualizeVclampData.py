'''
PROGRAM THAT PLOTS A VOLTAGE-CLAMP DATA FOR A GIVEN ABF FILE, FOR A SPECIFIED SWEEP


Created by Sayaka (Saya) Minegishi with assistance from ChatGPT
minegishis@brandeis.edu
Jul 16 2024


'''
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
import addCursor


# Function to apply low-pass filter
def low_pass_filter(trace, SampleRate, cutoff=300, order=5):
    nyquist = 0.5 * SampleRate
    normal_cutoff = cutoff / nyquist
    b, a = scipy.signal.butter(order, normal_cutoff, btype='low', analog=False)
    filtered_trace = scipy.signal.filtfilt(b, a, trace)
    return filtered_trace


######### Ask user input (automatic - no need to change any code here) #########
app = QApplication([])
file_paths, _ = QFileDialog.getOpenFileName(None, "Select file", "", "ABF Files (*.abf);;All Files (*)")

print(f"Selected file: {file_paths}")


# Ask for sweep number
sweepn, ok = QInputDialog.getText(None, "Enter Sweep Number", "Enter the sweep number to analyze:")

if not ok:
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Warning)
    msg.setText("No sweep number entered. Please enter a sweep number.")
    msg.setWindowTitle("Warning")
    msg.exec_()
    exit()
sweepn = int(sweepn)-1


    

#plot trace

abfdata = pyabf.ABF(file_paths)
abfdata.setSweep(sweepn)

# Visualize data


fig, ax = plt.subplots()
# Assuming addCursor.CursorClass is a valid class you have defined elsewhere
cursorobj = addCursor.CursorClass(ax, abfdata.sweepX, abfdata.sweepY) # create a CursorClass object for this graph

cid = fig.canvas.mpl_connect('motion_notify_event', cursorobj.mouse_event)

ax.plot(abfdata.sweepX, abfdata.sweepY, lw=2, color='green')
ax.set_xlabel('Time (s)')
ax.set_ylabel('Current (pA)') 
ax.set_title('Original Data')
ax.legend() 

plt.show()