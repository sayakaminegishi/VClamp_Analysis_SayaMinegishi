import numpy as np

def get_peak_amplitude(denoised_trace, time, starttime, endtime, baseline, inputVoltage):

    mask1 = (time >= starttime) & (time <= endtime)
    filtered_values = denoised_trace[mask1]  # trace values, for the hyperpolarizing step
    filtered_time = time[mask1]

    peak_val = np.max(filtered_values)  #peak current
    index_of_peak = np.argmax(filtered_values) 
    peak_loc = filtered_time[index_of_peak]  

    peakamp = peak_val - baseline
    areaundercurve_dep = np.trapz(filtered_values, filtered_time) #area under the curve
    vAtPeak = inputVoltage[index_of_peak] #input voltage at the time of the peak
