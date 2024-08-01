import pyabf
import matplotlib.pyplot as plt
import numpy as np
import os
import numpy as np
import scipy.optimize
import scipy.signal
import matplotlib.pyplot as plt
import pyabf
import pandas as pd
import traceback
import logging
from PyQt5.QtWidgets import QApplication, QFileDialog, QInputDialog, QMessageBox, QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel
from getFilePath import get_file_path  # type: ignore
from get_tail_times import getStartEndTail, getDepolarizationStartEnd, get_last_sweep_number
from remove_abf_extension import remove_abf_extension  # type: ignore
from getTailCurrentModel import getExpTailModel
from getFilePath import get_only_filename
from apply_low_pass_filter_FUNCTION import low_pass_filter
import re
from get_base_filename import get_base_filename


protocolname="BradleyShort"
# Start and end times of voltage steps, in seconds
st, en = getDepolarizationStartEnd(protocolname)

######## AFTER 1PBC ###########
abf = pyabf.ABF("/Users/sayakaminegishi/Documents/Birren Lab/CaCC project/DATA_Ephys/FOR ANALYSIS/1PBC experiments/SHR cells/datashr/7_24_SHRN/2024_07_24_02_0014.abf")
time =  np.array(abf.sweepX)
# Convert these to indices
stindx = np.argmin(np.abs(time - st))  # Closest index to start time
enidx = np.argmin(np.abs(time - en))   # Closest index to end time

# pt1 = int(en-0.005) * abf.dataPointsPerMs

# pt2 = int(en * abf.dataPointsPerMs)

currents = []
voltages = []
for sweep in abf.sweepList:
    abf.setSweep(sweep)
    currents.append(np.average(abf.sweepY[stindx:enidx]))
    voltages.append(abf.sweepC)

plt.figure(figsize=(8, 5))
plt.grid(alpha=.5, ls='--')
plt.plot(voltages, currents, '.-', ms=15)
plt.ylabel(abf.sweepLabelY)
plt.xlabel(abf.sweepLabelC)
plt.title(f"I/V Relationship of {abf.abfID}")

plt.show()