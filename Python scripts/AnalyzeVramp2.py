#Analyze Vramp 2
#This program estimates the reversal potential of a current from a given ramp.
#TO USER: specify filepath, starttime, and endtime of the region to analyze (the linear part of the ramp).

#TODO: FIND WHY THE GRAPH IS NOT UPDATING TO NEW SWEEP AT EACH ITERATION

# Created by Sayaka (Saya) Minegishi
# Contact: minegishis@brandeis.edu
# Last modified: June 16 2024

import pyabf
import matplotlib.pyplot as plt
import numpy as np
from scipy import interpolate
from scipy import optimize
import pandas as pd

##### USER-DEFINED INPUT DATA ############
filepath = "/Users/sayakaminegishi/Documents/Birren Lab/CaCC project/DATA_Ephys/2024_06_06_01_0005.abf"  # file to analyze
starttime = 0.3547 #start of region of interest (the linear part in command) (sec)
endtime = 1.7538  #end of region of interest (sec)

#################################################
abfdata = pyabf.ABF(filepath)

# Print information about the ABF file
print(abfdata)  # gives info about abfdata, such as no. of sweeps, channels, duration

# initialize summary table for recording data
columns = ['sweep_number', 'a', 'b'] #column headers
df = pd.DataFrame(columns = columns) #create an empty dataframe with the specified columns


# Iterate over all sweeps
for i in abfdata.sweepList:
    swp = i
    abfdata.setSweep(swp)

    # Extract sweep data and convert them to arrays
    t = np.array(abfdata.sweepX)
    x = np.array(abfdata.sweepC)  #voltage values
    y = np.array(abfdata.sweepY)  # Current values

    #design a mapping function to fit a line to the data - in this case a line
    def objective(x, a, b):
        return a*x + b
    

    #use curve_fit() to fit the defined curve in the Objective() to the dataset
    mask = (t>=starttime) & (t<=endtime) #region to analyze, in indices for t
    initialguess = [5, 3]
    # fit curve to the CURRENT vs t DATA
    fit, covariance = optimize.curve_fit(objective, t[mask], y[mask],initialguess)
    a, b = fit
    #print equation of the fitted curve
    print('y = %.5f * x + %.5f' % (a, b)) #.5 specifies that the floating-point number should be formatted with 5 digits after the decimal point.

    #visualize fitted curve

    plt.scatter(t, y, label="data")
    x_fit = np.linspace(t[mask].min(), t[mask].max(), 100) #x values for line of best fit
    y_fit = objective(x_fit, *fit) #y values for fitted curve (i.e line of best fit)
    plt.plot(x_fit, y_fit, c="red", label="fit")
    plt.legend()
    plt.show()

    #add sweep, a and b to the summary table
    new_row = {'sweep_number': i, 'a':  a, 'b': b}
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)




    

#get summary data
print("Recorded fit, y = a*x+b")
print(df) #show the recorded data

#calculate the mean of each column
column_means = df.mean()

#print the means
print("\nMean of each column for this cell:")
print(column_means) #use column_means['var'] to access specific column val

meana = column_means['a']
meanb = column_means['b']

# Print the averaged line of best fit
print(f"averaged line of best fit: y_avg = {meana:.5f} * x + {meanb:.5f}")


#calculate reversal potential!

x_int = -meanb/meana #x-int, in time
#find point in Vm vs t closest to x_int

# Compute the absolute differences
differences = np.abs(x - x_int)

# Find the index of the minimum difference
index_of_min = np.argmin(differences)

# Retrieve the closest value
closest_value = x[index_of_min]

print(f"The reversal potential of cell is approximately {closest_value} mV.")




