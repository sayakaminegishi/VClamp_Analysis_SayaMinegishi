''' OKADA Ca2+ dependence analysis - AUC & AMP
computes peak amplitude & area under curve for the EACH sweep, where the duration
of depolarization increases with increasing sweep number.

Created by: Sayaka (Saya) Minegishi
Contact: minegishis@brandeis.edu
Last modified: June 17 2024
'''

import numpy as np
import scipy.optimize
import scipy.signal
import matplotlib.pyplot as plt
import pyabf
import pandas as pd
import traceback
import logging
from PyQt5.QtWidgets import QApplication, QFileDialog

# Function to apply low-pass filter
def low_pass_filter(trace, SampleRate, cutoff=300, order=5):
    nyquist = 0.5 * SampleRate
    normal_cutoff = cutoff / nyquist
    b, a = scipy.signal.butter(order, normal_cutoff, btype='low', analog=False)
    filtered_trace = scipy.signal.filtfilt(b, a, trace)
    return filtered_trace


######### Ask user input (automatic - no need to change any code here) #########
app = QApplication([])
options = QFileDialog.Options()
file_paths, _ = QFileDialog.getOpenFileNames(None, "Select files", "", "ABF Files (*.abf);;All Files (*)", options=options)

print(f"Selected files: {file_paths}")

#depolarization start time
starttime = 0.0967

filesnotworking = []

# Initialize summary table for recording data
columns = ['Filename', 'Sweep_number', 'Peak_amplitude(pA)', 'Input_voltage(mV)','AreaUnderCurve(pA*mV)']  # column headers
df = pd.DataFrame(columns=columns)  # create an empty dataframe with the specified columns


for file in file_paths:
   
        print("\nWorking on " + file)

        abfdata = pyabf.ABF(file)
        durationdiff = 0.2125 - 0.1132 #TODO: double check with pclamp protocol
        peakamps = [] 
        depdurationlist = []    
        areaundercurve_deplist = []   
        for swp in abfdata.sweepList:
            try:
                abfdata.setSweep(swp)

                #get duration of depolarization for the sweep (i.e. find endtime)
                depDuration = (durationdiff * swp) 
                endtime = depDuration  + 0.1132
                depdurationlist.append(depDuration)

                # Visualize data
                plt.figure()
                plt.plot(abfdata.sweepX, abfdata.sweepY, color="orange")
                plt.xlabel('Time (s)')
                plt.ylabel('Current (pA)') 
                plt.title('Original Data')
                plt.legend() 
                plt.show()

                # Extract sweep data and convert them to arrays
                time = np.array(abfdata.sweepX)
                trace = np.array(abfdata.sweepY)  # Current values
                inputv = np.array(abfdata.sweepC)
                SampleRate = abfdata.dataRate  # sample rate in total samples per second per channel
                baseline = trace[0]

                # Denoise the trace
                denoised_trace = low_pass_filter(trace, SampleRate)

                # Get peak amplitude
                mask1 = (time >= starttime) & (time <= endtime)
                filtered_values = denoised_trace[mask1]  # trace values, for the hyperpolarizing step
                filtered_time = time[mask1]

                peak_val = np.max(filtered_values)  #peak current
                index_of_peak = np.argmax(filtered_values) 
                peak_loc = filtered_time[index_of_peak]  

                peakamp = peak_val - baseline
                areaundercurve_dep = np.trapz(filtered_values, filtered_time) #area under the curve
                vAtPeak = inputv[index_of_peak] #input voltage at the time of the peak
                peakamps.append(peakamp)
                areaundercurve_deplist.append(areaundercurve_dep)

                if peakamp is not None and areaundercurve_dep is not None and vAtPeak is not None:
                    # Add filename, peakamp and areaundercurve, and voltage input to summary table

                    new_row = {'Filename': file, 'Sweep_number': swp, 'Peak_amplitude(pA)': peakamp, 'Input_voltage(mV)': vAtPeak, 'AreaUnderCurve(pA*mV)': areaundercurve_dep}
                    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                   
                
            except Exception as e:
                filesnotworking.append(file)
                logging.error(traceback.format_exc())  # log error

        #PLOT RESULTS - stacked subplot
        fig, axs = plt.subplots(2, 1)
        axs[0].plot(depdurationlist,peakamps)
        axs[0].set_title('Input Voltage Duration(ms) vs. Peak current amplitude(pA)')
        axs[1].plot(depdurationlist, areaundercurve_deplist, 'tab:green')
        axs[1].set_title('Input voltage duration (ms) vs area under curve(pA*ms)')

        for ax in axs.flat:
            ax.set(xlabel='x-label', ylabel='y-label')

        # Hide x labels and tick labels for top plots and y ticks for right plots.
        for ax in axs.flat:
            ax.label_outer()

# Get summary data for the cell
print(df)  # show the recorded data

# Show files not working
string = ','.join(str(x) for x in filesnotworking)
print("Files not working:" + string)


