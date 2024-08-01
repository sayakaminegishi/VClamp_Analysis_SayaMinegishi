#created by Sayaka (Saya) Minegishi with the help of chatGPT
import pyabf
import matplotlib.pyplot as plt
import numpy as np
from get_tail_times import getDepolarizationStartEnd


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


protocolname = "BradleyShort"

# Start and end times of voltage steps, in seconds
st, en = getDepolarizationStartEnd(protocolname)

# Create a figure for the combined plot
plt.figure(figsize=(8, 5))

# Plot AFTER 1PBC
abf = pyabf.ABF("/Users/sayakaminegishi/Documents/Birren Lab/CaCC project/DATA_Ephys/FOR ANALYSIS/1PBC experiments/fig3/wkytreat/2024_07_17_03_0008.abf")
time = np.array(abf.sweepX)

# Convert these to indices
stindx = np.argmin(np.abs(time - st))  # Closest index to start time
enidx = np.argmin(np.abs(time - en))   # Closest index to end time

currents_after = []
voltages_after = []

for sweep in abf.sweepList:
    abf.setSweep(sweep)
    currents_after.append(np.average(abf.sweepY[stindx:enidx]))
    voltages_after.append(abf.sweepC[stindx])  # Capture the command voltage at the start index

# setting font sizeto 30
plt.rcParams.update({'font.size': 28})
 
plt.plot(voltages_after, currents_after, '.-', ms=15, label='After 1PBC', color = "orange")

# Plot BEFORE 1PBC
abf = pyabf.ABF("/Users/sayakaminegishi/Documents/Birren Lab/CaCC project/DATA_Ephys/FOR ANALYSIS/1PBC experiments/fig3/WKYcontrol/2024_07_17_03_0006.abf")
time = np.array(abf.sweepX)

# Convert these to indices
stindx = np.argmin(np.abs(time - st))  # Closest index to start time
enidx = np.argmin(np.abs(time - en))   # Closest index to end time

currents_before = []
voltages_before = []

for sweep in abf.sweepList:
    abf.setSweep(sweep)
    currents_before.append(np.average(abf.sweepY[stindx:enidx]))
    voltages_before.append(abf.sweepC[stindx])  # Capture the command voltage at the start index

plt.plot(voltages_before, currents_before, '.-', ms=15, label='Before 1PBC', color="blue")

# Add labels, title, legend, and grid
plt.grid(alpha=.5, ls='--')
plt.ylabel(abf.sweepLabelY, fontweight="bold")
plt.xlabel(abf.sweepLabelC, fontweight="bold")
plt.title(f"I/V Relationship of an SHR with Cd+, TTX, 1PBC", fontweight="bold")
plt.legend()

# Show the plot
plt.show()

#calculate reversal potentials
rev_before = estimate_reversal_potential(voltages_before, currents_before)
rev_after = estimate_reversal_potential(voltages_after, currents_after)

print("The reversal potential before 1PBC:" + str(rev_before))
print("%fThe reversal potential after 1PBC: " + str(rev_after))
