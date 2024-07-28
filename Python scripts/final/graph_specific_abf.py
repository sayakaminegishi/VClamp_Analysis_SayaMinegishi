import pyabf
from plotSweepsAndCommand import plotAllSweepsAndCommand
import matplotlib.pyplot as plt

file = '/Users/sayakaminegishi/Documents/Birren Lab/CaCC project/DATA_Ephys/FOR ANALYSIS/1PBC experiments/WKY cells/wkydata/7_17_WKYN/2024_07_17_03_0002.abf'
abf = pyabf.ABF(file)
abf.setSweep(10)

#graph
base_filename= "SHRN- all sweeps"
saved = "/Users/sayakaminegishi/MATLAB/Projects/VClamp_Analysis_SayaMinegishi"
plotAllSweepsAndCommand(abf, base_filename, saved)


# print(abf.sweepY) # displays sweep data (ADC)
# print(abf.sweepX) # displays sweep times (seconds)
# print(abf.sweepC) # displays command waveform (DAC)


# plt.plot(abf.sweepX, abf.sweepY)
# plt.show()