'''
NO FITTING!!!
CREATE IV CURVE FOR CONTROL AND TREATMENT FILE(S), takes AVERAGE for each Voltage, fits a CURVE, AND PLOTS THEM ON THE SAME AXES.
FINDS ESTIMATED REVERSAL POTENTIAL FOR CONTROL AND TREATMENT GROUPS.


This script processes ABF files.

Note: Ensure all selected files use the SAME PROTOCOL TYPE, and the SAME CELL. 


#TODO: make it make and take average of all IV curves from different cells and average them. use big for loop for each cell. 
#TODO: ADD TAU!!!!!

NOTES: interpolation is used for missing/unreadable data points, so the results may vary from reality for high voltages.

Created by: Sayaka (Saya) Minegishi with some help from ChatGPT.
Contact: minegishis@brandeis.edu
Date: July 16, 2024

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

#analyzes one file - gives one entry of voltage, current, conductance
def IV_nolineofbestfit(filename, protocolname):
    # filename = path to file
    abf = pyabf.ABF(filename)
    SampleRate = abf.dataRate

    # Loop through sweeps and process each one
    #steady state arrays:
    currents = []
    voltages = []
    conductances = []

    #peak-based arrays
    currents_pk = []
    voltages_pk = []
    conductances_pk = []
    
    
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

        ############## STEADY STATE - Extract current and voltage at the end index #########################
        curr = denoised_trace[enidx-3]  # Current for the depolarizing step
        volt = abf.sweepC[enidx-3]  # Voltage for the depolarizing step
        conduc = curr / volt if volt != 0 else np.nan  # Conductance for the depolarizing step, avoid division by zero

        # Store the data - STEADY STATE
        currents.append(curr)
        voltages.append(volt)
        conductances.append(conduc)

        ######### PEAK-BASED IV ###############################
        pk_idx = np.argmax(denoised_trace[stindx:enidx]) + stindx 
        curr_pk = denoised_trace[pk_idx]  # Current for the depolarizing step
        volt_pk = abf.sweepC[pk_idx]  # Voltage for the depolarizing step
        conduc_pk = curr_pk / volt_pk if volt_pk != 0 else np.nan  # Conductance for the depolarizing step, avoid division by zero

        # Store the data - STEADY STATE
        currents_pk.append(curr_pk)
        voltages_pk.append(volt_pk)
        conductances_pk.append(conduc_pk)


    # Return a dictionary with the IV data. Steady-state voltage, current and conductance from each sweep (so for each Voltage level)
    #STEADY-STATE
    iv_data = {
        "voltages_ss": voltages,
        "currents_ss": currents,
        "conductances_ss": conductances,
    }

    #IV CURVE BASED ON PEAK CURRENT FOR EACH SWEEP
    iv_data_pk = {
        "voltages_pk": voltages_pk,
        "currents_pk": currents_pk,
        "conductances_pk": conductances_pk,
    }


    return iv_data, iv_data_pk

# Function to average IV curves for steady-state IVs
def average_iv_curve_ss(iv_data_collection, common_voltages):
    interpolated_currents = []

    for iv_data in iv_data_collection:
        voltages = np.array(iv_data['voltages_ss'])
        currents = np.array(iv_data['currents_ss'])

        # Interpolate currents to the common voltage points
        interpolated_current = np.interp(common_voltages, voltages, currents)
        interpolated_currents.append(interpolated_current)

    # Average the interpolated currents
    avg_currents = np.nanmean(interpolated_currents, axis=0)

    return avg_currents

# Function to average IV curves for steady-state IVs
def average_iv_curve_pk(iv_data_collection, common_voltages):
    interpolated_currents = []

    for iv_data in iv_data_collection:
        voltages = np.array(iv_data['voltages_pk'])
        currents = np.array(iv_data['currents_pk'])

        # Interpolate currents to the common voltage points
        interpolated_current = np.interp(common_voltages, voltages, currents)
        interpolated_currents.append(interpolated_current)

    # Average the interpolated currents
    avg_currents = np.nanmean(interpolated_currents, axis=0)

    return avg_currents





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

#arrays to store files for analysis
iv_data_collection_control_ss = [] #stores the dictionary containing IV properties from ith file. a list of dictionaries
iv_data_collection_treat_ss = [] #stores the dictionary containing IV properties from ith file. a list of dictionaries
iv_data_collection_control_pk = [] #stores the dictionary containing IV properties from ith file. a list of dictionaries
iv_data_collection_treat_pk = [] #stores the dictionary containing IV properties from ith file. a list of dictionaries

filesnotworking = []

########### MAIN PROGRAM ###############
n_control = len(sorted_file_paths_control) #number of control files
n_treat = len(sorted_file_paths_treat) #number of treat files

# Control files
for file in sorted_file_paths_control:
    try:
        iv_data_ss, iv_data_pk = IV_nolineofbestfit(file, protocolname)
        iv_data_collection_control_ss.append(iv_data_ss)
        iv_data_collection_control_pk.append(iv_data_pk)

    except Exception as e:
        filesnotworking.append(file)
        logging.error(traceback.format_exc())  # log error

# Treatment files
for file in sorted_file_paths_treat:
    try:
        iv_data_ss, iv_data_pk = IV_nolineofbestfit(file, protocolname)
        iv_data_collection_treat_ss.append(iv_data_ss)
        iv_data_collection_treat_pk.append(iv_data_pk)
        
    except Exception as e:
        filesnotworking.append(file)
        logging.error(traceback.format_exc())  # log error


#GET CELL NAME
f = sorted_file_paths_treat[0] #full directory path of 1st treatment file
cell_name = get_base_filename(f)

# Define a common voltage range for interpolation
common_voltages = np.linspace(-100, 100, 100)  # Adjust this range based on your protocol

# Calculate the average IV curves
avg_currents_control_ss = average_iv_curve_ss(iv_data_collection_control_ss, common_voltages)
avg_currents_treat_ss = average_iv_curve_ss(iv_data_collection_treat_ss, common_voltages)

avg_currents_control_pk = average_iv_curve_pk(iv_data_collection_control_pk, common_voltages)
avg_currents_treat_pk = average_iv_curve_pk(iv_data_collection_treat_pk, common_voltages)

######### REVERSAL POTENTIAL ####################
def estimate_reversal_potential(voltages, currents):
    # Find indices where current crosses zero
    zero_crossings = np.where(np.diff(np.sign(currents)))[0]
    
    if len(zero_crossings) == 0:
        return np.nan  # No zero crossing found
    
    # Take the first zero crossing for simplicity
    idx = zero_crossings[0]
    
    # Points around the zero crossing
    V1, I1 = voltages[idx], currents[idx]
    V2, I2 = voltages[idx + 1], currents[idx + 1]
    
    # Linear interpolation to find V where I = 0
    reversal_potential = V1 - (I1 * (V2 - V1)) / (I2 - I1)
    return reversal_potential

# Estimate reversal potentials
rev_potential_control_ss = estimate_reversal_potential(common_voltages, avg_currents_control_ss)
rev_potential_treat_ss = estimate_reversal_potential(common_voltages, avg_currents_treat_ss)
rev_potential_control_pk = estimate_reversal_potential(common_voltages, avg_currents_control_pk)
rev_potential_treat_pk = estimate_reversal_potential(common_voltages, avg_currents_treat_pk)

print("Estimated reversal potential (Control - Steady State): {:.2f} mV".format(rev_potential_control_ss))
print("Estimated reversal potential (Treatment - Steady State): {:.2f} mV".format(rev_potential_treat_ss))
print("Estimated reversal potential (Control - Peak Current): {:.2f} mV".format(rev_potential_control_pk))
print("Estimated reversal potential (Treatment - Peak Current): {:.2f} mV".format(rev_potential_treat_pk))

############### PLOTTING #############

# Plot I/V curve
fig, ax = plt.subplots() 

ax.plot(common_voltages, avg_currents_control_ss, '-',color='orange', label = "Control - Steady State")
ax.plot(common_voltages, avg_currents_treat_ss, '--', color = '#ff9966', label = "Treatment - Steady State") #replace Treatment with name of drug (1PBC)

ax.plot(common_voltages, avg_currents_control_pk, '-', color = 'green', label = "Control - Peak Current") #replace Treatment with name of drug (1PBC)
ax.plot(common_voltages, avg_currents_treat_pk, '--', color = '#5cd65c', label = "Treatment - Peak Current") #replace Treatment with name of drug (1PBC)


# Mark reversal potentials
ax.axvline(rev_potential_control_ss, color='orange', linestyle=':', label='Reversal Potential (Control - SS)')
ax.axvline(rev_potential_treat_ss, color='#ff9966', linestyle=':', label='Reversal Potential (Treatment - SS)')
ax.axvline(rev_potential_control_pk, color='green', linestyle=':', label='Reversal Potential (Control - PK)')
ax.axvline(rev_potential_treat_pk, color='#5cd65c', linestyle=':', label='Reversal Potential (Treatment - PK)')


ax.set_xlabel('Voltage (mV)')
ax.set_ylabel('Current (pA)') 
ax.set_title("Averaged and Fitted I/V Relationship for {}".format(cell_name))
ax.legend() 




# Save the plot as a JPEG file
os.makedirs(save_directory, exist_ok = True) #check that directory exists, create it if doesn't

#create the image file name
imgname = 'iv_curve_{}.jpeg'.format(cell_name) #name of image file exported

#FULL PATH to save the image
save_path = os.path.join(save_directory, imgname)

# save as jpeg
plt.savefig(save_path, format = 'jpeg')

plt.show()


#alternatively: savePltAsJpeg(...)

########## REVERSAL POTENTIAL ESTIMATION ##################


# Show completion message as a dialog box
msg = QMessageBox()
msg.setIcon(QMessageBox.Information)
msg.setText("Program complete")
msg.setWindowTitle("Information")
msg.setStandardButtons(QMessageBox.Ok)
msg.exec_()