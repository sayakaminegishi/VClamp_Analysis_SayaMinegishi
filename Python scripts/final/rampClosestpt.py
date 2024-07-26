'''Analyze Vramp 5 - THE CLOSEST PT METHOD
the reversal potential is interpolated from the values closest to I = 0
'''

import os
import numpy as np
import matplotlib.pyplot as plt
import pyabf
import pandas as pd
from PyQt5.QtWidgets import QApplication, QFileDialog, QInputDialog, QMessageBox
from getFilePath import get_file_path  # type: ignore
from get_tail_times import getStartEndTail, getDepolarizationStartEnd, get_last_sweep_number
from remove_abf_extension import remove_abf_extension  # type: ignore
from getTailCurrentModel import getExpTailModel
from getFilePath import get_only_filename
from apply_low_pass_filter_FUNCTION import low_pass_filter
from get_base_filename import get_base_filename

def showInstructions(messagetoshow):
    # Show given message as a dialog box
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Information)
    msg.setText(messagetoshow)
    msg.setWindowTitle("Information")
    msg.setStandardButtons(QMessageBox.Ok)
    msg.exec_()

##### USER-DEFINED INPUT DATA ############
starttime = 0.3547  # start of region of interest (the linear part in command) (sec)
endtime = 1.7538  # end of region of interest (sec)

app = QApplication([])
protocolname = "Vramp"

# Select Vramp file
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

# Load the ABF file
abfdata = pyabf.ABF(filepath)
sweepn_last = get_last_sweep_number(protocolname)
valid_sweeps = set(range(sweepn_last))  # Set of valid sweep indices

if sweepn == "all":
    sweepnum_array_final = list(valid_sweeps)
elif ":" in sweepn:
    parts = sweepn.split(":")
    a = int(parts[0]) - 1
    b = int(parts[1])
    sweepnum_array_final = [i for i in range(a, b) if i in valid_sweeps]
elif "," in sweepn:
    sweepnum_array = [int(x) - 1 for x in sweepn.split(",")]
    sweepnum_array_final = [x for x in sweepnum_array if x in valid_sweeps]
else:
    sweepnum_array_final = [int(sweepn) - 1]
    if sweepnum_array_final[0] not in valid_sweeps:
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setText(f"Sweep number {sweepnum_array_final[0] + 1} is out of range. Please enter valid sweep numbers.")
        msg.setWindowTitle("Warning")
        msg.exec_()
        exit()

# Initialize lists to collect data for averaging
all_voltages = []
all_currents = []

# Iterate over all sweeps, average out ramp from each sweep into one
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
    denoised_trace = low_pass_filter(y, abfdata.dataRate)

    # Use curve_fit() to fit the defined curve in the model_func to the dataset
    mask = (time >= starttime) & (time <= endtime)  # region to analyze

    voltages = x[mask]
    currents = denoised_trace[mask]

    # Collect data for averaging
    all_voltages.append(voltages)
    all_currents.append(currents)

# Check if any valid data was collected
if not all_voltages or not all_currents:
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Warning)
    msg.setText("No valid sweeps available for analysis. Exiting.")
    msg.setWindowTitle("Warning")
    msg.exec_()
    exit()

# Average the collected data
avg_voltages = np.mean(all_voltages, axis=0)
avg_currents = np.mean(all_currents, axis=0)

# Find the voltage where the current is closest to zero
def interpolate_reversal_potential(voltage, current):
    # Find the index of the current value closest to zero
    closest_idx = np.argmin(np.abs(current))
    
    # If the closest current is exactly zero, return the corresponding voltage
    if current[closest_idx] == 0:
        return voltage[closest_idx]
    
    # Interpolate between the closest points
    if closest_idx == 0:
        return voltage[closest_idx]
    elif closest_idx == len(current) - 1:
        return voltage[closest_idx]
    
    # Linearly interpolate to find the voltage where current crosses zero
    x0, x1 = voltage[closest_idx - 1], voltage[closest_idx]
    y0, y1 = current[closest_idx - 1], current[closest_idx]
    return x0 - (x1 - x0) * (y0 / (y1 - y0))

reversal_potential = interpolate_reversal_potential(avg_voltages, avg_currents)
print("Estimated Reversal Potential: {:.2f} mV".format(reversal_potential))

# Plot I/V curve
plt.figure(figsize=(12, 6))
plt.plot(avg_voltages, avg_currents, 'o', label='Averaged Data')
plt.axhline(0, color='black', linestyle='-')
# plt.axvline(0, color='black', linestyle='-', label = "y=0")


# plt.plot(reversal_potential, color = 'red', marker = '*', label='Estimated reversal potential')
plt.axhline(0, color='gray', linestyle='--')
plt.axvline(reversal_potential, color='red', linestyle='--', label='Estimated Reversal Potential')


plt.title("Averaged I/V Relationship for {}".format(get_base_filename(filepath)))
plt.xlabel("Voltage (mV)")
plt.ylabel("Current (pA)")
plt.legend()
plt.tight_layout()

# Save the plot as a JPEG file
imgname = 'iv_curve_{}.jpeg'.format(get_base_filename(filepath))
plt.savefig(imgname, format='jpeg')

# Display the plot
plt.show()
