import os
import numpy as np
import scipy.optimize
import matplotlib.pyplot as plt
import pyabf
import pandas as pd
from PyQt5.QtWidgets import QApplication, QFileDialog, QInputDialog, QMessageBox
from get_tail_times import get_last_sweep_number
from remove_abf_extension import remove_abf_extension  # type: ignore
from get_base_filename import get_base_filename
from apply_low_pass_filter_FUNCTION import low_pass_filter

def showInstructions(messagetoshow):
    # Show given message as a dialog box
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Information)
    msg.setText(messagetoshow)
    msg.setWindowTitle("Information")
    msg.setStandardButtons(QMessageBox.Ok)
    msg.exec_()

# Estimate the reversal potential based on fitted curve
def estimate_reversalVm(params):
    roots = np.roots(params)
    real_roots = [root for root in roots if np.isreal(root)]
    real_roots = np.real(real_roots)
    closest_root = min(real_roots, key=lambda x: abs(x - 0))
    return closest_root

# Design a mapping function to fit a degree 7 polynomial to the data
def model_func(x, a, b, c, d, e, f, g, h):
    return a * x**7 + b * x**6 + c * x**5 + d * x**4 + e * x**3 + f * x**2 + g * x + h

# Function to get the fitted equation as a string
def get_polynomial_equation(params):
    terms = ["{:.2e}x^{}".format(params[i], 7 - i) for i in range(len(params))]
    equation = " + ".join(terms)
    return "I = " + equation

# User-defined input data
starttime = 0.3547  # Start of region of interest (sec)
endtime = 1.7538  # End of region of interest (sec)

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
sweepn, ok = QInputDialog.getText(None, "Enter Sweep Numbers", "Enter Sweep Numbers separated by ',', a:b for range a to b, or 'all' for all sweeps")

if not ok:
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Warning)
    msg.setText("No sweep number entered. Please enter a sweep number.")
    msg.setWindowTitle("Warning")
    msg.exec_()
    exit()

if sweepn == "all":
    sweepn_last = get_last_sweep_number(protocolname)
    sweepnum_array_final = [i - 1 for i in range(1, sweepn_last + 1)]
elif ":" in sweepn:
    parts = sweepn.split(":")
    a = int(parts[0])
    b = int(parts[1])
    sweepnum_array_final = list(range(a - 1, b))
elif "," in sweepn:
    sweepnum_array = [int(x) for x in sweepn.split(",")]
    sweepnum_array_final = [x - 1 for x in sweepnum_array]
else:
    sweepnum_array_final = [int(sweepn) - 1]

abfdata = pyabf.ABF(filepath)
SampleRate = abfdata.dataRate
print(abfdata)

cell_name = get_base_filename(filepath)

all_voltages = []
all_currents = []

for i in sweepnum_array_final:
    try:
        abfdata.setSweep(i)
    except ValueError:
        print(f"Sweep {i + 1} not available (must be 0 - {abfdata.sweepCount - 1}). Skipping this sweep.")
        continue

    time = np.array(abfdata.sweepX)
    x = np.array(abfdata.sweepC)
    y = np.array(abfdata.sweepY)

    denoised_trace = low_pass_filter(y, SampleRate)
    mask = (time >= starttime) & (time <= endtime)
    voltages = x[mask]
    currents = denoised_trace[mask]

    all_voltages.append(voltages)
    all_currents.append(currents)

if not all_voltages or not all_currents:
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Warning)
    msg.setText("No valid sweeps available. Exiting.")
    msg.setWindowTitle("Warning")
    msg.exec_()
    exit()

avg_voltages = np.mean(all_voltages, axis=0)
avg_currents = np.mean(all_currents, axis=0)

# Sort the currents and voltages by the sorted order of the currents
sorted_indices = np.argsort(avg_currents)
sorted_voltages = avg_voltages[sorted_indices]
sorted_currents = avg_currents[sorted_indices]

# Initial guess for polynomial parameters
initial_guess = [0] * 8  # 8 parameters for 7th-degree polynomial

params, _ = scipy.optimize.curve_fit(model_func, sorted_voltages, sorted_currents, p0=initial_guess)
fitted_curve = model_func(sorted_voltages, *params)

equationcurve = get_polynomial_equation(params)
print("IV Curve Equation:")
print(equationcurve)

plt.figure(figsize=(12, 6))
plt.plot(sorted_voltages, sorted_currents, 'o', label='Averaged Data')
plt.plot(sorted_voltages, fitted_curve, '-', label='Fitted Curve')

plt.title("Averaged and Fitted I/V Relationship for {}".format(cell_name))
plt.xlabel("Voltage (mV)")
plt.ylabel("Current (pA)")
plt.legend()

plt.tight_layout()
imgname = 'iv_curve_{}.jpeg'.format(cell_name)
plt.savefig(imgname, format='jpeg')
plt.show()

# Estimate the reversal potential
reversal_potential = estimate_reversalVm(params)
print("Estimated Reversal Potential: {:.2f} mV".format(reversal_potential))
