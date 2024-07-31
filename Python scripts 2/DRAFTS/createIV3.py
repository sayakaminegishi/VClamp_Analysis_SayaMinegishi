#creates an IV curve from a given abf file
# Created by: Sayaka (Saya) Minegishi
# June 23 2024

# Creates an IV curve from a given ABF file
# Created by: Sayaka (Saya) Minegishi
# June 23 2024

# Creates an IV curve from a given ABF file
# Created by: Sayaka (Saya) Minegishi
# June 23 2024

import pyabf
import matplotlib.pyplot as plt
import numpy as np
from get_tail_times import getDepolarizationStartEnd
from apply_low_pass_filter_FUNCTION import low_pass_filter

def find_line_of_bestFit(x1,y1,x2,y2):
    """
    Calculate the equation of a line given two points.

    (x1,y1) = first point on the line
    (x2,y2) = second point on line
   
    """
    if x1 == x2:
        raise ValueError("The two points have the same x-coordinate, resulting in a vertical line.")
    
    # Calculate the slope (m)
    m = (y2 - y1) / (x2 - x1)
    
    # Calculate the y-intercept (b)
    b = y1 - m * x1
    
    return m, b

def createIV3(filename, protocolname):
    # filename = path to file
    abf = pyabf.ABF(filename)
    SampleRate = abf.dataRate

    # Loop through sweeps and process each one
    currents = []
    voltages = []
    conductances = []

    for sweep in abf.sweepList:
        abf.setSweep(sweep)
        
        # Extract raw sweep data
        time = np.array(abf.sweepX)
        trace = np.array(abf.sweepY)

        # Denoise the trace
        denoised_trace = low_pass_filter(trace, SampleRate) #low_pass_filter can only accept 1D data, which is trace, NOT an abf object

        # Start and end times of voltage steps, in seconds
        st, en = getDepolarizationStartEnd(protocolname)

        # Convert these to indices
        stindx = np.argmin(np.abs(time - st))  # Closest index to start time
        enidx = np.argmin(np.abs(time - en))   # Closest index to end time
        midpointidx = int((stindx + enidx) / 2)  # Midpoint index

        # Extract current and voltage at the midpoint index
        curr = denoised_trace[midpointidx]  # Current for the depolarizing step
        volt = abf.sweepC[midpointidx]  # Voltage for the depolarizing step
        conduc = curr / volt if volt != 0 else np.nan  # Conductance for the depolarizing step, avoid division by zero

        # Store the data
        currents.append(curr)
        voltages.append(volt)
        conductances.append(conduc)

    

    # Find the reversal potential (voltage at which current is 0)
    revVm = None
    for i in range(1, len(currents)):
        if currents[i-1] * currents[i] <= 0:
            # Linear interpolation to find the exact voltage where current is 0 -- between index i and i-1
            #reversal_potential = voltages[i-1] - currents[i-1] * (voltages[i] - voltages[i-1]) / (currents[i] - currents[i-1])

           
            if abf.sweepC[i] == abf.sweepC[i-1]:
                revVm = abf.sweepC[i] #reversal potential
            else:
                m,b = find_line_of_bestFit(abf.sweepC[i-1], abf.sweepY[i-1], abf.sweepC[i], abf.sweepY[i])  #draw a straight line between i and i-1
                #line of best fit: y = mx + b
                #find x intercept
                revVm = -b/m 
            
    else:
        m = None
        b = None

            

    if revVm is not None:
        print(f"The reversal potential is approximately {revVm:.2f} mV")

    # Return a dictionary with the IV data
    iv_data = {
        "voltages": voltages,
        "currents": currents,
        "conductances": conductances,
        "reversal_potential": revVm
    }

    # Plot I/V curve
    plt.figure(figsize=(8, 5))
    plt.grid(alpha=.5, ls='--')
    plt.plot(voltages, currents, '.-', ms=15)
    
    plt.ylabel(abf.sweepLabelY)
    plt.xlabel("Voltage (mV)")
    plt.title(f"I/V Relationship of {abf.abfID}")

    # if revVm is not None:
    #     plt.plot(abf.sweepC, m*(abf.sweepC) + b, color = "green", ls = ".-")
    #     plt.plot(revVm, 0, 'ro')

    # plt.show()  

    if revVm is not None and m is not None and b is not None:
        # Plot the line of best fit
        fit_line_x = np.array(voltages)
        fit_line_y = m * fit_line_x + b
        plt.plot(fit_line_x, fit_line_y, color="green", linestyle="--", label="Line of Best Fit")
        plt.plot(revVm, 0, 'ro', label="Reversal Potential")
        plt.legend()

    plt.show()


    return iv_data

####################

filename = "/Users/sayakaminegishi/Documents/Birren Lab/CaCC project/DATA_Ephys/2024_06_21_02_0007.abf"
protocol = "BradleyShort"
dict = createIV3(filename, protocol)

