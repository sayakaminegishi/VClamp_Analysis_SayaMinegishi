import pyabf
import matplotlib.pyplot as plt

# Load and plot data for SHR control
file_control = '/Users/sayakaminegishi/Documents/Birren Lab/CaCC project/DATA_Ephys/FOR ANALYSIS/1PBC experiments/fig3/SHR control/2024_07_24_02_0009.abf'
abf_control = pyabf.ABF(file_control)
abf_control.setSweep(10)

# Load and plot data for SHR treated
file_treat = '/Users/sayakaminegishi/Documents/Birren Lab/CaCC project/DATA_Ephys/FOR ANALYSIS/1PBC experiments/fig3/SHR treat/2024_07_24_02_0015.abf'
abf_treat = pyabf.ABF(file_treat)
abf_treat.setSweep(10)

# Determine the common axis limits
x_min = min(min(abf_control.sweepX), min(abf_treat.sweepX))
x_max = max(max(abf_control.sweepX), max(abf_treat.sweepX))
y_min = min(min(abf_control.sweepY), min(abf_treat.sweepY))
y_max = max(max(abf_control.sweepY), max(abf_treat.sweepY)) + 100

# Create figure and subplots
fig, axs = plt.subplots(1, 2, figsize=(14, 6)) #1 row, 2 columns so horizontally aligned

# Plot SHR control data
axs[0].plot(abf_control.sweepX, abf_control.sweepY)
axs[0].set_title('SHR Control')
axs[0].set_xlabel('Time (sec)')
axs[0].set_ylabel('Current (pA)')
axs[0].set_xlim([x_min, x_max])
axs[0].set_ylim([y_min, y_max])

# Plot SHR treated data
axs[1].plot(abf_treat.sweepX, abf_treat.sweepY)
axs[1].set_title('SHR Treated')
axs[1].set_xlabel('Time (sec)')
axs[1].set_ylabel('Current (pA)')
axs[1].set_xlim([x_min, x_max])
axs[1].set_ylim([y_min, y_max])

# Adjust layout and show plot
plt.tight_layout()
plt.show()
