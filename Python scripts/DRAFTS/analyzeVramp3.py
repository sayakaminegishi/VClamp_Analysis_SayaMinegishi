#Analyze Vramp 3
#This program estimates the reversal potential of a current from a given ramp.
#TO USER: specify filepath, starttime, and endtime of the region to analyze (the linear part of the ramp).

#TODO: FIND WHY THE GRAPH IS NOT UPDATING TO NEW SWEEP AT EACH ITERATION

# Created by Sayaka (Saya) Minegishi
# Contact: minegishis@brandeis.edu
# Last modified: July 13 2024

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

#design a mapping function to fit a line to the data - in this case a line
def model_func(x, a, b, c, d):
    return a * x**3 + b * x**2 + c * x + d


# Function to get the fitted equation as a string
def get_polynomial_equation(params):
    terms = ["{:.2e}x^{}".format(params[i], 3 - i) for i in range(len(params))] #params[i] are the coefficients of the polynomial
    equation = " + ".join(terms)
    return "I = " + equation


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
 


    

##### USER-DEFINED INPUT DATA ############
filepath = "/Users/sayakaminegishi/Documents/Birren Lab/CaCC project/DATA_Ephys/2024_06_06_01_0005_NilWN_1-5mMCa.abf"  # file to analyze
starttime = 0.3547 #start of region of interest (the linear part in command) (sec)
endtime = 1.7538  #end of region of interest (sec)

#################################################
abfdata = pyabf.ABF(filepath)
SampleRate = abfdata.dataRate
# Print information about the ABF file
print(abfdata)  # gives info about abfdata, such as no. of sweeps, channels, duration

# initialize summary table for recording data
columns = ['sweep_number', 'a', 'b'] #column headers
df = pd.DataFrame(columns = columns) #create an empty dataframe with the specified columns
 #GET CELL NAME
    
cell_name = get_base_filename(filepath)


# Iterate over all sweeps. average out ramp from each sweep into one
for i in abfdata.sweepList:
    swp = i
    abfdata.setSweep(swp)

    # Extract sweep data and convert them to arrays
    time = np.array(abfdata.sweepX)
    x = np.array(abfdata.sweepC)  #voltage values
    y = np.array(abfdata.sweepY)  # Current values

    # Denoise the trace
    denoised_trace = low_pass_filter(y, SampleRate) #low_pass_filter can only accept 1D data, which is trace, NOT an abf object

    #use curve_fit() to fit the defined curve in the Objective() to the dataset
    #mask = (t>=starttime) & (t<=endtime) #region to analyze, in indices for t
    
    st, en = starttime, endtime

    # Fit the model to the averaged data
   
    #  Define a common voltage range for interpolation  
    common_voltages = np.linspace(-100, 100, 100)  # Adjust this range based on your protocol

    params, _ = scipy.optimize.curve_fit(model_func, common_voltages, y)
    
    # Generate fitted curves
    fitted_curve = model_func(common_voltages, *params) #* for argument unpacking. unpacks list to individual arguments.
    

    # Get the equations of the fitted curves
    equationcurve = get_polynomial_equation(params)
   

    print("IV Curve Equation:")
    print(equationcurve)
   



# Plot I/V curve
plt.figure(figsize=(12, 6))

# Plot averaged Control data
plt.plot(common_voltages, y, 'o', label='Control Data')
plt.plot(common_voltages, fitted_curve, '-', label='Control Fit')

plt.title("Averaged and Fitted I/V Relationship for {}".format(cell_name))
plt.xlabel("Voltage (mV)")
plt.ylabel("Current (pA)")

plt.legend()

plt.tight_layout()


# Save the plot as a JPEG file
imgname = 'iv_curve_{}.jpeg'.format(cell_name) #name of image file exported
plt.savefig(imgname, format='jpeg')

# Display the plot
plt.show()


