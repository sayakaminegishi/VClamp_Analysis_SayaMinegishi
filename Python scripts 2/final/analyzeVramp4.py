
'''Analyze Vramp 4
This program fits a degree 3 polynomial curve to a series of Vramp recordings from a single abf file,
and estimates the reversal potential of a current from a given ramp based on the fitted curve.


# Created by Sayaka (Saya) Minegishi with some assistance from ChatGPT
# Contact: minegishis@brandeis.edu
# Last modified: July 13 2024
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
from PyQt5.QtWidgets import QApplication, QFileDialog, QInputDialog, QMessageBox, QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel
from getFilePath import get_file_path  # type: ignore
from get_tail_times import getStartEndTail, getDepolarizationStartEnd, get_last_sweep_number
from remove_abf_extension import remove_abf_extension  # type: ignore
from getTailCurrentModel import getExpTailModel
from getFilePath import get_only_filename
from apply_low_pass_filter_FUNCTION import low_pass_filter
import re
from get_base_filename import get_base_filename


def showInstructions(messagetoshow):
    # Show given message as a dialog box
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Information)
    msg.setText(messagetoshow)
    msg.setWindowTitle("Information")
    msg.setStandardButtons(QMessageBox.Ok)
    msg.exec_()

# Design a mapping function to fit a line to the data - in this case a line
def model_func(x, a, b, c, d):
    return a * x**3 + b * x**2 + c * x + d

# Function to get the fitted equation as a string
def get_polynomial_equation(params):
    terms = ["{:.2e}x^{}".format(params[i], 3 - i) for i in range(len(params))]  # params[i] are the coefficients of the polynomial
    equation = " + ".join(terms)
    return "I = " + equation

# Estimate the reversal potential based on fitted curve
def estimate_reversalVm(params):
    # params = array of coefficients
    roots = np.roots(params)  # find the roots of the polynomial (i.e. where I = 0)
    
    # Print only real-number roots
    real_roots = [root for root in roots if np.isreal(root)]  # filter out real roots
    real_roots = np.real(real_roots)

    # Find the root closest to V=0
    closest_root = min(real_roots, key=lambda x: abs(x - 0))

    return closest_root  # estimated reversal potential

##### USER-DEFINED INPUT DATA ############
#filepath = "/Users/sayakaminegishi/Documents/Birren Lab/CaCC project/DATA_Ephys/2024_06_06_01_0005_NilWN_1-5mMCa.abf"  # file to analyze

#below start and end times are default for my specific Vramp protocol
starttime = 0.3547  # start of region of interest (the linear part in command) (sec)
endtime = 1.7538  # end of region of interest (sec)

app = QApplication([])
protocolname = "Vramp"

# Select control files
showInstructions("Select Vramp file to analyze")

filepath, _ = QFileDialog.getOpenFileName(None, "Select Vramp file", "", "ABF Files (*.abf);;All Files (*)")

if not filepath:
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Warning)
    msg.setText("No file selected. Please select a file.")
    msg.setWindowTitle("Warning")
    msg.exec_()
    exit()

# Ask for sweep numbers to analyze
sweepn, ok = QInputDialog.getText(None, "Enter Sweep Numbers", 
                                  "Enter Sweep Numbers separated by ',', a:b for range a to b, or enter 'all' for all sweeps ")

if not ok:
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Warning)
    msg.setText("No sweep number entered. Please enter a sweep number.")
    msg.setWindowTitle("Warning")
    msg.exec_()
    exit()

if sweepn == "all":
    # Assuming sweepn is the string returned by get_last_sweep_number(protocolname)
    sweepn_last = get_last_sweep_number(protocolname)
    sweepnum_array_final = [i - 1 for i in range(1, sweepn_last+1)]

elif(sweepn.find(":")!=-1):
    #string contains ":"
    parts = sweepn.split(":") #split the numbers before and after

    #convert each part to int
    a = int(parts[0])
    b = int(parts[1])
    # Create an array [a, b]
    sweepnum_array_final = list(range(a-1, b)) 

elif(sweepn.find(",")!=-1):
    sweepnumber = sweepn

    # Convert comma-separated string to list of integers
    sweepnum_array = [int(x) for x in sweepnumber.split(",")]

    # Subtract 1 from each element in the list
    sweepnum_array_final = [x - 1 for x in sweepnum_array]
else:
    # Convert comma-separated string to list of integers
    sweepnum_array_final = [int(sweepn)-1]



#################################################
abfdata = pyabf.ABF(filepath)
SampleRate = abfdata.dataRate
# Print information about the ABF file
print(abfdata)  # gives info about abfdata, such as no. of sweeps, channels, duration


#df = pd.DataFrame(columns=columns)  # create an empty dataframe with the specified columns
# GET CELL NAME
cell_name = get_base_filename(filepath)

# Initialize lists to collect data for averaging
all_voltages = []
all_currents = []

# Iterate over all sweeps, average out ramp from each sweep into one - gives error if invalid sweep number
for i in sweepnum_array_final:
    try:
        abfdata.setSweep(i)
    except ValueError:
        print(f"Sweep {i + 1} is invalid. Skipping this sweep.")
        continue

    # Extract sweep data and convert them to arrays
    time = np.array(abfdata.sweepX)
    x = np.array(abfdata.sweepC)  # voltage values
    y = np.array(abfdata.sweepY)  # current values

    # Denoise the trace
    denoised_trace = low_pass_filter(y, SampleRate)  # low_pass_filter can only accept 1D data, which is trace, NOT an abf object

    # Use curve_fit() to fit the defined curve in the model_func to the dataset
    mask = (time >= starttime) & (time <= endtime)  # region to analyze, in indices for time

    voltages = x[mask]
    currents = denoised_trace[mask]

    # Collect data for averaging
    all_voltages.append(voltages)
    all_currents.append(currents)

# Average the collected data
avg_voltages = np.mean(all_voltages, axis=0)
avg_currents = np.mean(all_currents, axis=0)

# Fit the model to the averaged data
params, _ = scipy.optimize.curve_fit(model_func, avg_voltages, avg_currents)

# Generate fitted curves
fitted_curve = model_func(avg_voltages, *params)  # * for argument unpacking. unpacks list to individual arguments.

# Get the equations of the fitted curves
equationcurve = get_polynomial_equation(params)

print("IV Curve Equation:")
print(equationcurve)

# Estimate the reversal potential
reversal_potential = estimate_reversalVm(params)
print("Estimated Reversal Potential: {:.2f} mV".format(reversal_potential))

# Plot I/V curve
plt.figure(figsize=(12, 6))

# Plot averaged Control data
plt.plot(avg_voltages, avg_currents, 'o', label='Averaged Data')
plt.plot(avg_voltages, fitted_curve, '-', label='Fitted Curve')

plt.title("Averaged and Fitted I/V Relationship for {}".format(cell_name))
plt.xlabel("Voltage (mV)")
plt.ylabel("Current (pA)")

plt.legend()

plt.tight_layout()

# Save the plot as a JPEG file
imgname = 'iv_curve_{}.jpeg'.format(cell_name)  # name of image file exported
plt.savefig(imgname, format='jpeg')

# Display the plot
plt.show()
