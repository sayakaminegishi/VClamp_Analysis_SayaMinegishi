'''
CREATE IV CURVE FOR CONTROL AND TREATMENT FILE(S), takes AVERAGE for each Voltage, fits a CURVE, AND PLOTS THEM ON THE SAME AXES.
FINDS ESTIMATED REVERSAL POTENTIAL FOR CONTROL AND TREATMENT GROUPS.

This script processes ABF files.

Note: Ensure all selected files use the SAME PROTOCOL TYPE.

#TODO: make it make and take average of all IV curves from different cells and average them. use big for loop for each cell. 

NOTES: interpolation is used for missing/unreadable data points, so the results may vary from reality for high voltages.

Created by: Sayaka (Saya) Minegishi with some help from ChatGPT.
Contact: minegishis@brandeis.edu
Date: July 12, 2024

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
from PyQt5.QtWidgets import QApplication, QFileDialog, QInputDialog, QMessageBox, QWidget
from getFilePath import get_file_path  # type: ignore
from get_tail_times import getStartEndTail, getDepolarizationStartEnd, get_last_sweep_number
from remove_abf_extension import remove_abf_extension  # type: ignore
from getTailCurrentModel import getExpTailModel
from getFilePath import get_only_filename
from apply_low_pass_filter_FUNCTION import low_pass_filter


def showInstructions(messagetoshow):
    # Show given message as a dialog box
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Information)
    msg.setText(messagetoshow)
    msg.setWindowTitle("Information")
    msg.setStandardButtons(QMessageBox.Ok)
    msg.exec_()

#analyzes one file - gives one entry of voltage, current, conductance
def IV_nolineofbestfit(filename, protocolname):
    # filename = path to file
    abf = pyabf.ABF(filename)
    SampleRate = abf.dataRate

    # Loop through sweeps and process each one
    currents = []
    voltages = []
    conductances = []
    
    for sweep in abf.sweepList:
        abf.setSweep(sweep)
        
        # Extract raw sweep data
        time = np.array(abf.sweepX)
        trace = np.array(abf.sweepY)

        # Denoise the trace
        denoised_trace = low_pass_filter(trace, SampleRate) #low_pass_filter can only accept 1D data, which is trace, NOT an abf object

        # Start and end times of voltage steps, in seconds
        st, en = getDepolarizationStartEnd(protocolname)

        # Convert these to indices
        stindx = np.argmin(np.abs(time - st))  # Closest index to start time
        enidx = np.argmin(np.abs(time - en))   # Closest index to end time

        # Extract current and voltage at the end index
        curr = denoised_trace[enidx-3]  # Current for the depolarizing step
        volt = abf.sweepC[enidx-3]  # Voltage for the depolarizing step
        conduc = curr / volt if volt != 0 else np.nan  # Conductance for the depolarizing step, avoid division by zero

        # Store the data
        currents.append(curr)
        voltages.append(volt)
        conductances.append(conduc)

    # Return a dictionary with the IV data
    iv_data = {
        "voltages": voltages,
        "currents": currents,
        "conductances": conductances,
    }
    
    return iv_data

# Function to average IV curves
def average_iv_curve(iv_data_collection, common_voltages):
    interpolated_currents = []

    for iv_data in iv_data_collection:
        voltages = np.array(iv_data['voltages'])
        currents = np.array(iv_data['currents'])

        # Interpolate currents to the common voltage points
        interpolated_current = np.interp(common_voltages, voltages, currents)
        interpolated_currents.append(interpolated_current)

    # Average the interpolated currents
    avg_currents = np.nanmean(interpolated_currents, axis=0)

    return avg_currents


#estimate the reversal potential based on fitted curve
def estimate_reversalVm(params):
    #params = array of coefficients
    roots = np.roots(params) #find the roots of the polynomial (i.e. where I = 0)
    
    #print only real-number roots
    real_roots = [root for root in roots if np.isreal(root)] #filter out real roots
    real_roots = np.real(real_roots)

  
    # Find the root closest to V=0
    closest_root = min(real_roots, key=lambda x: abs(x - 0))

    return closest_root #estimated reversal potential
 

# Function to get the fitted equation as a string
def get_polynomial_equation(params):
    terms = ["{:.2e}x^{}".format(params[i], 3 - i) for i in range(len(params))] #params[i] are the coefficients of the polynomial
    equation = " + ".join(terms)
    return "I = " + equation

####################
##### FILE SELECTION
# Main script
app = QApplication([])

# Select control files
showInstructions("Select control files")
options = QFileDialog.Options()

file_paths_control, _ = QFileDialog.getOpenFileNames(None, "Select control files", "", "ABF Files (*.abf);;All Files (*)", options=options)

if not file_paths_control:
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Warning)
    msg.setText("No file selected. Please select a file.")
    msg.setWindowTitle("Warning")
    msg.exec_()
    exit()

sorted_file_paths_control = sorted(file_paths_control)

# Select treatment files (eg blocker)
showInstructions("Select treatment files")
options = QFileDialog.Options()
file_paths_treat, _ = QFileDialog.getOpenFileNames(None, "Select treatment files", "", "ABF Files (*.abf);;All Files (*)", options=options)

if not file_paths_treat:
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Warning)
    msg.setText("No file selected. Please select a file.")
    msg.setWindowTitle("Warning")
    msg.exec_()
    exit()
sorted_file_paths_treat = sorted(file_paths_treat)

# Select directory to save Excel files
showInstructions("Select directory to save summary files")
save_directory = QFileDialog.getExistingDirectory(None, "Select Directory to Save Excel Files", options=options)

# Ask for protocol type
protocol_types = ["Henckels", "BradleyLong", "BradleyShort"]
protocolname, ok = QInputDialog.getItem(None, "Select Protocol Type", "Enter the protocol type:", protocol_types, 0, False)

if not ok:
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Warning)
    msg.setText("No protocol type selected. Please select a protocol type.")
    msg.setWindowTitle("Warning")
    msg.exec_()
    exit()

iv_data_collection_control = [] #stores the dictionary containing IV properties from ith file. a list of dictionaries
iv_data_collection_treat = [] #stores the dictionary containing IV properties from ith file. a list of dictionaries
filesnotworking = []

########### MAIN PROGRAM ###############
n_control = len(sorted_file_paths_control) #number of control files
n_treat = len(sorted_file_paths_treat) #number of treat files

# Control files
for file in sorted_file_paths_control:
    try:
        iv_data = IV_nolineofbestfit(file, protocolname)
        iv_data_collection_control.append(iv_data)
    except Exception as e:
        filesnotworking.append(file)
        logging.error(traceback.format_exc())  # log error

# Treatment files
for file in sorted_file_paths_treat:
    try:
        iv_data = IV_nolineofbestfit(file, protocolname)
        iv_data_collection_treat.append(iv_data)
    except Exception as e:
        filesnotworking.append(file)
        logging.error(traceback.format_exc())  # log error


# Define a common voltage range for interpolation
common_voltages = np.linspace(-100, 100, 100)  # Adjust this range based on your protocol

# Calculate the average IV curves
avg_currents_control = average_iv_curve(iv_data_collection_control, common_voltages)
avg_currents_treat = average_iv_curve(iv_data_collection_treat, common_voltages)

################ CURVE FITTING ############
#define a degree3 polynomial model function to fit our data to.
def model_func(x, a, b, c, d):
    return a * x**3 + b * x**2 + c * x + d

# Fit the model to the averaged data
params_control, _ = scipy.optimize.curve_fit(model_func, common_voltages, avg_currents_control)
params_treat, _ = scipy.optimize.curve_fit(model_func, common_voltages, avg_currents_treat)

# Generate fitted curves
fitted_curve_control = model_func(common_voltages, *params_control) #* for argument unpacking. unpacks list to individual arguments.
fitted_curve_treat = model_func(common_voltages, *params_treat)


# Get the equations of the fitted curves
equation_control = get_polynomial_equation(params_control)
equation_treat = get_polynomial_equation(params_treat)

print("Control IV Curve Equation:")
print(equation_control)
print("\nTreatment IV Curve Equation:")
print(equation_treat)

############### PLOTTING #############

# Plot I/V curve
plt.figure(figsize=(12, 6))

# Plot averaged Control data
plt.plot(common_voltages, avg_currents_control, 'o', label='Control Data')
plt.plot(common_voltages, fitted_curve_control, '-', label='Control Fit')

# Plot averaged Treatment data
plt.plot(common_voltages, avg_currents_treat, 'x', label='Treatment Data')
plt.plot(common_voltages, fitted_curve_treat, '--', label='Treatment Fit')

plt.title("Averaged and Fitted I/V Relationship (Control vs. Treatment)")
plt.xlabel("Voltage (mV)")
plt.ylabel("Current (pA)")

# # LEGEND - add no. of points  (no. of recordings from this cell)
# additional_text = 'n_control={} \nn_treatment = {}'.format(str(n_control), str(n_treat))

# # Create a legend with custom handles and labels
# handles, labels = plt.gca().get_legend_handles_labels()
# handles.append(additional_text)  # Add additional text as a handle
# labels.append('Number of points')  # Add label for the additional text

# plt.legend(handles=handles, labels=labels)
plt.legend()

plt.tight_layout()

# Display the plot
plt.show()

########## REVERSAL POTENTIAL ESTIMATION ##################

#reversal potential for control
revVmControl = estimate_reversalVm(params_control)

#estimate the reversal potential for treatment
revVmTreatment = estimate_reversalVm(params_treat)

print("The reversal potential of the control group is {} mV".format(str(revVmControl)))
print("The reversal potential of the treatment group is {} mV".format(str(revVmTreatment)))

# Show completion message as a dialog box
msg = QMessageBox()
msg.setIcon(QMessageBox.Information)
msg.setText("Program complete")
msg.setWindowTitle("Information")
msg.setStandardButtons(QMessageBox.Ok)
msg.exec_()