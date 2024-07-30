import pyabf
from plotSweepsAndCommand import plotAllSweepsAndCommand
import matplotlib.pyplot as plt

file = '/Users/sayakaminegishi/Documents/Birren Lab/CaCC project/DATA_Ephys/FOR ANALYSIS/1PBC experiments/fig3/SHR control/2024_07_24_02_0007.abf'
abf = pyabf.ABF(file)
abf.setSweep(10)

# #graph all sweeps:
# base_filename= "SHRN- all sweeps"
# saved = "/Users/sayakaminegishi/MATLAB/Projects/VClamp_Analysis_SayaMinegishi"
# plotAllSweepsAndCommand(abf, base_filename, saved)


#graph a single sweep:
print(abf.sweepY) # displays sweep data (ADC)
print(abf.sweepX) # displays sweep times (seconds)
print(abf.sweepC) # displays command waveform (DAC)


plt.plot(abf.sweepX, abf.sweepY)
plt.xlabel("time (sec)")
plt.ylabel("current (pA)")
plt.show() 



file = '/Users/sayakaminegishi/Documents/Birren Lab/CaCC project/DATA_Ephys/FOR ANALYSIS/1PBC experiments/fig3/SHR treat/2024_07_24_02_0014.abf'
abf = pyabf.ABF(file)
abf.setSweep(10)

# #graph all sweeps:
# base_filename= "SHRN- all sweeps"
# saved = "/Users/sayakaminegishi/MATLAB/Projects/VClamp_Analysis_SayaMinegishi"
# plotAllSweepsAndCommand(abf, base_filename, saved)


#graph a single sweep:
print(abf.sweepY) # displays sweep data (ADC)
print(abf.sweepX) # displays sweep times (seconds)
print(abf.sweepC) # displays command waveform (DAC)


plt.plot(abf.sweepX, abf.sweepY)
plt.xlabel("time (sec)")
plt.ylabel("current (pA)")
plt.show() 

