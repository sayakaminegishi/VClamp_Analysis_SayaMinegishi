''' PEAK CURRENT ANALYSIS - AUC and AMP
computes peak amplitude & area under curve for the greatest current step, for a specified protocol (with vsteps), and compares (gives avg) across multiple vclamp files.
Can be used to get average peak current properties for one strain. Can be ran 2 times to compare differences between two strains.

This script gives the PEAK, not necessarily the steady-state current.

Works for Henckels & Bradley Protocols.

Created by: Sayaka (Saya) Minegishi
Contact: minegishis@brandeis.edu
Last modified: June 18 2024

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
from get_tail_times import getDepolarizationStartEnd
from get_protocol_name import get_protocol_name # type: ignore
import os
from get_base_filename import get_base_filename


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

# Ask protocol type
protocolname = str(input("Enter the protocol type - Henckels, BradleyLong or BradleyShort: "))

# Define peak time
k = 0 #since not Okada
starttime, endtime = getDepolarizationStartEnd(protocolname) #get tail start and end times


filesnotworking = []

# Initialize summary table for recording data
columns = ['Filename', 'Peak_amplitude(pA)', 'Input_voltage(mV)','AreaUnderCurve(pA*mV)']  # column headers
df = pd.DataFrame(columns=columns)  # create an empty dataframe with the specified columns
save_directory = QFileDialog.getExistingDirectory(None, "Select Directory to Save Excel Files", options=options)


for file in file_paths:
    try:
        print("\nWorking on " + file)

        abfdata = pyabf.ABF(file)
        swp = len(abfdata.sweepList)-1 #analyze the last sweep
        abfdata.setSweep(swp)
        base_filename= get_base_filename(file) #get shortened filename

        # Visualize data
        plt.figure()
        plt.plot(abfdata.sweepX, abfdata.sweepY, color="orange")
        plt.xlabel('Time (s)')
        plt.ylabel('Current (pA)') 
        plt.title('Original Data for {}'.format(base_filename))
        
        

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

        ##FOR_DEBUGGING##
        plt.plot(peak_loc, peak_val, 'o') #show peak loc
        plt.show()



        peakamp = peak_val - baseline
        areaundercurve_dep = np.trapz(filtered_values, filtered_time) #area under the curve
        vAtPeak = inputv[index_of_peak] #input voltage at the time of the peak

        if peakamp is not None and areaundercurve_dep is not None and vAtPeak is not None:
            # Add filename, peakamp and areaundercurve, and voltage input to summary table
           
            new_row = {'Filename': file, 'Peak_amplitude(pA)': peakamp, 'Input_voltage(mV)': vAtPeak, 'AreaUnderCurve(pA*mV)': areaundercurve_dep}
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    except Exception as e:
        filesnotworking.append(file)
        logging.error(traceback.format_exc())  # log error

# Get summary data for the cell
print(df)  # show the recorded data

print("\nMean of each column:")

mean_a = df['Peak_amplitude(pA)'].mean()
mean_b = df['Input_voltage(mV)'].mean()
mean_c = df['AreaUnderCurve(pA*mV)'].mean()

print("Mean peak amplitude(pA): " + str(mean_a))
print("Mean Input_voltage(mV): " + str(mean_b))
print("Mean area under curve(mV*pA): " + str(mean_c))

# Export all the dataframes from all the files analyzed to a single Excel file
# Construct the file name
summary_excelname = os.path.join(save_directory, f"PeakAmplitude_{protocolname}_sweep{swp}.xlsx")

# Use ExcelWriter to save the DataFrame to an Excel file
with pd.ExcelWriter(summary_excelname, engine='xlsxwriter') as writer:
    
    df.to_excel(writer, sheet_name=protocolname, index=False)


# Show files not working
string = ','.join(str(x) for x in filesnotworking)
print("Files not working:" + string)


