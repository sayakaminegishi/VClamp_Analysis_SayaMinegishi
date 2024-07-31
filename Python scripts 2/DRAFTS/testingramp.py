import os
import numpy as np
import scipy.optimize
import scipy.signal
import matplotlib.pyplot as plt
import pyabf
import pandas as pd
import traceback
import logging
from scipy.interpolate import interp1d
from scipy.stats import zscore
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
    sweepnum_array_final = [i - 1 for i in range(1, sweepn_last + 1)]

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

# Iterate over all sweeps, average out ramp from each sweep into one
for i in sweepnum_array_final:
    swp = i
    abfdata.setSweep(swp)

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

# Remove outliers using Z-score method
z_scores = zscore(avg_currents)
filtered_indices = np.abs(z_scores) < 3  # Consider data points with Z-score < 3 as non-outliers

filtered_voltages = avg_voltages[filtered_indices]
filtered_currents = avg_currents[filtered_indices]

# Remove inf and NaN values
finite_indices = np.isfinite(filtered_currents)

filtered_voltages = filtered_voltages[finite_indices]
filtered_currents = filtered_currents[finite_indices]

# Create a unique interpolated function for filtered data
interp_func = interp1d(filtered_voltages, filtered_currents, kind='linear', fill_value='extrapolate')

# Generate unique y-values for the x-values
unique_currents = interp_func(filtered_voltages)

# Fit the model to the filtered data
params, _ = scipy.optimize.curve_fit(model_func, filtered_voltages, unique_currents)

# Generate fitted curves
fitted_curve = model_func(filtered_voltages, *params)  # * for argument unpacking. unpacks list to individual arguments.

# Get the equations of the fitted curves
equationcurve = get_polynomial_equation(params)

print("IV Curve Equation:")
print(equationcurve)

# Estimate the reversal potential
reversal_potential = estimate_reversalVm(params)
print("Estimated Reversal Potential: {:.2f} mV".format(reversal_potential))

# Plot I/V curve
plt.figure(figsize=(12, 6))

# Plot filtered Control data
plt.plot(filtered_voltages, filtered_currents, 'o', label='Filtered Averaged Data')
plt.plot(filtered_voltages, fitted_curve, '-', label='Fitted Curve')

plt.title("Filtered and Fitted I/V Relationship for {}".format(cell_name))
plt.xlabel("Voltage (mV)")
plt.ylabel("Current (pA)")

plt.legend()

plt.tight_layout()

# Save the plot as a JPEG file
imgname = 'iv_curve_{}.jpeg'.format(cell_name)  # name of image file exported
plt.savefig(imgname, format='jpeg')

# Display the plot
plt.show()
