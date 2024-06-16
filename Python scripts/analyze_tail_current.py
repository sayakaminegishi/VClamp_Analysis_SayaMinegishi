#analyze tail current
# Created by Sayaka (Saya) Minegishi
# Contact: minegishis@brandeis.edu
# Last modified Jun 15 2024

import numpy as np
import scipy.optimize
import matplotlib.pyplot as plt



def analyze_tail(time, trace, HypStart, HypEnd, sweep, SampleRate):
    #time = time vector, trace = whole data to analuyze, hypstart = start time of hyperpolarization step, hypend = end time of tail current
    #hypstart and hypend are in SECONDS. sweep = sweep number

    # stIdx = np.where(time==HypStart) #index of sttart time with respect to the oriignal trace
    # edIdx = np.where(time==HypEnd) #FIND THE CLOSEST CORRESPONDING PT
    


    stIdx = np.abs(time - HypStart).argmin()

    print("Index of closest starting value:", stIdx)
    print("Closest value:", time[stIdx])

    edIdx = np.abs(time - HypEnd).argmin()

    print("Index of closest end value:", edIdx)
    print("Closest value (s):", time[edIdx])


    tail_i_whole= trace[stIdx:edIdx] #extract tail region
    tail_time_vec = time[stIdx:edIdx] #time vector

    print(stIdx, edIdx)
    print(tail_i_whole)
    #split the tail current into 2 sections about the trough
    #find trough:
    #FROM HERE, WE'RE WORKING WITH ZOOMED UP (EXTRACTED) TRACE!! 
    
    # Check if the list is not empty before finding the minimum value
 
    min_current = min(tail_i_whole)
    print("Minimum current:", min_current)
   

    minlocIdx = np.abs(tail_i_whole - min_current).argmin()
    min_loc_time = tail_time_vec[minlocIdx]

    ##### Aside: convereting these to time with respect to the original trace for later use:
    min_loc_idx_real = minlocIdx + stIdx #REAL minimum current time index
    min_loc_time_real = time[min_loc_idx_real] #REAL minimum current time (sec)
    ###### Aside End ##########

    tail_prior_vals = trace[stIdx:min_loc_idx_real] #current data values for start of hyp. step to trough
    tail_post_vals = trace[min_loc_idx_real: edIdx] #data values from trough to end of tail
    
    #fit exponential model to tail_prior and tail_post independently

    ###POST - work with respect to the ORIIGINAL TRACE
    xs = time[min_loc_idx_real:edIdx]
    ys = tail_post_vals

    # Plot original data for the tail current - POST
    fig3 = plt.figure()
    plt.plot(xs, ys, '.')
    plt.title("Tail current for Sweep " + str(sweep))

    ##### FIT EXPONENTIAL TO POST - perform the fit
    #p0 = (2000, .1, 50) # start with values near those we expect
    #params, cv = scipy.optimize.curve_fit(monoExp, xs, ys, p0)

    def monoExp(x, m, t, b):
        return -m * np.exp(-t * x) + b
    
    mask = (t>=starttime) & (t<=endtime)
    params, cv = scipy.optimize.curve_fit(monoExp, xs, ys)
    m, t, b = params
    tauSec = (1 / t) / SampleRate

    # determine quality of the fit
    squaredDiffs = np.square(ys - monoExp(xs, m, t, b))
    squaredDiffsFromMean = np.square(ys - np.mean(ys))
    rSquared = 1 - np.sum(squaredDiffs) / np.sum(squaredDiffsFromMean)
    print(f"R² = {rSquared}")

    # plot the results
    plt.plot(xs, ys, '.', label="data")
    plt.plot(xs, monoExp(xs, m, t, b), '--', label="fitted")
    plt.title("Fitted Exponential Curve for Sweep " + str(sweep))
    plt.show()

    # inspect the parameters
    print("Sweep "+ str(sweep))
    print(f"Y = {m} * e^(-{t} * x) + {b}")
    print(f"Tau = {tauSec * 1e6} µs")






