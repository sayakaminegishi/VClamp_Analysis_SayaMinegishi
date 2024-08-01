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

# Create figure and axis
plt.figure(figsize=(10, 6))
plt.rcParams.update({'font.size': 24})

# Plot SHR control data
plt.plot(abf_control.sweepX, abf_control.sweepY, label='SHR Control', color='red', linewidth="2.5")

# Plot SHR treated data
plt.plot(abf_treat.sweepX, abf_treat.sweepY, label='SHR Treated', color='orange',linewidth="1.5")

# Add titles and labels
plt.title('SHR Control vs.1PBC', fontweight = "bold")
plt.xlabel('Time (sec)', fontweight = "bold")
plt.ylabel('Current (pA)', fontweight = "bold")
plt.xlim([x_min, 0.3])
plt.ylim([y_min, y_max])
plt.legend()

# Show plot
plt.tight_layout()
plt.show()
