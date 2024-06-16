#analyze tail current - MAIN. TODO: CHECK OUTPUTS WITH MENTOR
#this script fits an exponential curve of best fit to the tail current, from the minimum value to the end of tail.


# Created by Sayaka (Saya) Minegishi
# Contact: minegishis@brandeis.edu
# Last modified Jun 16 2024

import numpy as np
import scipy.optimize
import matplotlib.pyplot as plt
import pyabf
import matplotlib.pyplot as plt
import numpy as np
from scipy import interpolate
from scipy import optimize
import pandas as pd
import traceback
import logging

##### USER-DEFINED INPUT DATA ############
filepath = "/Users/sayakaminegishi/Documents/Birren Lab/CaCC project/DATA_Ephys/2024_06_06_01_0003.abf"  # file to analyze
starttime = 0.6 #start of the hyperpolarizing step leading to the tail current (includes the part BEFORE trough)
endtime = 1.5  #end of tail current, ie the hyperpolarizing step (sec)
#SampleRate = 20000 # in Hz

######################################
# Function to analyze the tail current (from trough to end of tail)
def analyze_tail(time, trace, trough, HypEnd, sweep, SampleRate):
    #time = time vector, trace = whole data to analuyze, hypstart = start time of hyperpolarization step, hypend = end time of tail current
    #hypstart and hypend are in SECONDS. sweep = sweep number

    # stIdx = np.where(time==HypStart) #index of sttart time with respect to the oriignal trace
    # edIdx = np.where(time==HypEnd) #FIND THE CLOSEST CORRESPONDING PT
    

    #fit exponential model to part of tail after trough

    #p0 = (2000, .1, 50) # start with values near those we expect
    #params, cv = scipy.optimize.curve_fit(monoExp, xs, ys, p0)


    def monoExp(x, m, t, b):
        return m * np.exp(t * x) + b
    
    mask = (time>=trough) & (time<=HypEnd) #region to analyze - from trough to end of tail
    #p0 = (2000, .1, 50) # initial guess

    params, cv = scipy.optimize.curve_fit(monoExp, time[mask], trace[mask])
    m, t, b = params
    tauSec = (1 / t) / SampleRate

    # determine quality of the fit
    squaredDiffs = np.square(trace - monoExp(time, m, t, b))
    squaredDiffsFromMean = np.square(trace - np.mean(trace))
    rSquared = 1 - np.sum(squaredDiffs) / np.sum(squaredDiffsFromMean)
    print(f"R² = {rSquared}")

    # plot the results
    plt.plot(time, trace, '.', label="data")
    plt.plot(time, monoExp(time, m, t, b), '--', label="fitted")
    plt.title("Fitted Exponential Curve for Sweep " + str(sweep))
    plt.show()

    # inspect the parameters
    print("Sweep "+ str(sweep))
    print(f"Y = {m} * e^({t} * x) + {b}")
    print(f"Tau = {tauSec * 1e6} µs")

    return m, t, b

    


########### MAIN PROGRAM ################
abfdata = pyabf.ABF(filepath)

print(abfdata)  # gives info about abfdata, such as no. of sweeps, channels, duration

# initialize summary table for recording data
columns = ['sweep_number', 'm', 't', 'b'] #column headers
df = pd.DataFrame(columns = columns) #create an empty dataframe with the specified columns


#Run - iterate over all sweeps in file
for i in abfdata.sweepList:
    swp = i
    abfdata.setSweep(swp)
    
    # Extract sweep data and convert them to arrays
    time = np.array(abfdata.sweepX)
    trace = np.array(abfdata.sweepY)  # Current values
    SampleRate = abfdata.dataRate #sample rate in total samples per second per channel

    #get trough

    # Filter the values within the time range
    mask1 = (time >= starttime) & (time <= endtime)
    filtered_values = trace[mask1] #trace values, for the hyperpolarizing step
    filtered_time = time[mask1]

    trough_val = np.min(filtered_values) #minimum value of tail current, in mV
    # Find the index of the minimum value
    index_of_min = np.argmin(filtered_values)
    # Retrieve the corresponding timestamp
    trough_loc = filtered_time[index_of_min] #trough location, in seconds


    try:
        mfound,tfound,bfound= analyze_tail(time, trace, trough_loc, endtime, i, SampleRate)
        #add sweep, m, t, b to the summary table
        new_row = {'sweep_number': i, 'm':  mfound, 't': tfound,'b': bfound}
        df = df.append(new_row, ignore_index = True)
    

    except Exception as e:
        logging.error(traceback.format_exc()) #log error
    
    




############# Get summary data for the cell ################

#get summary data
print("Recorded fit,  y= m * exp(t * x) + b")
print(df) #show the recorded data

#calculate the mean of each column
column_means = df.mean()

#print the means
print("\nMean of each column for this cell:")
print(column_means) #use column_means['var'] to access specific column val

meanm = column_means['m']
meant = column_means['t']
meanb = column_means['b']

# Print the averaged line of best fit
print(f"averaged line of best fit: y= {meanm} * exp({meant} * x) + {meanb}")





