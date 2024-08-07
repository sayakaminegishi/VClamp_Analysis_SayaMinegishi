''' PEAK CURRENT ANALYSIS - AUC and AMP (Peak Current)
computes peak amplitude & area under curve for the greatest current step, for a specified protocol (with vsteps), and compares (gives avg) across multiple vclamp files.
Can be used to get average peak current properties for one strain. Can be ran 2 times to compare differences between two strains.

Works for Henckels & Bradley Protocols.

Created by: Sayaka (Saya) Minegishi
Contact: minegishis@brandeis.edu
Last modified: June 17 2024

$FIX!!!!!!! tail current amp not dep.
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

starttime, endtime = getDepolarizationStartEnd(protocolname) #get dep start and end times


filesnotworking = []

# Initialize summary table for recording data
columns = ['Filename', 'Steady_state_amplitude(pA)', 'Peak_Amplitude(pA)' 'Input_voltage(mV)','AreaUnderCurve(pA*mV)']  # column headers
df = pd.DataFrame(columns=columns)  # create an empty dataframe with the specified columns
save_directory = QFileDialog.getExistingDirectory(None, "Select Directory to Save Excel Files", options=options)


for file in file_paths:
    try:
        print("\nWorking on " + file)

        abfdata = pyabf.ABF(file)
        swp = len(abfdata.sweepList)-1 #analyze the last sweep
        abfdata.setSweep(swp)
        
        # Visualize data
        plt.figure()
        plt.plot(abfdata.sweepX, abfdata.sweepY, color="orange")
        plt.xlabel('Time (s)')
        plt.ylabel('Current (pA)') 
        plt.title('Original Data')
        plt.legend() 

        # Extract sweep data and convert them to arrays
        time = np.array(abfdata.sweepX)
        trace = np.array(abfdata.sweepY)  # Current values
        inputv = np.array(abfdata.sweepC)
        SampleRate = abfdata.dataRate  # sample rate in total samples per second per channel
        baseline = trace[0]

        # Denoise the trace
        denoised_trace = low_pass_filter(trace, SampleRate)

        # Get STEADY-STATE amplitude
        mask1 = (time >= starttime) & (time <= endtime)
        filtered_values = denoised_trace[mask1]  # trace values, for the hyperpolarizing step
        filtered_time = time[mask1]

        ss_val = np.max(filtered_values)  #peak current
        index_of_ss = np.argmax(filtered_values) 
        ss_loc = filtered_time[index_of_ss]  

        ssamp = ss_val - baseline
        areaundercurve_dep = np.trapz(filtered_values, filtered_time) #area under the curve
        vAtss = inputv[index_of_ss] #input voltage at the time of the peak

        #get PEAK CURRENT amplitude


        if ssamp is not None and areaundercurve_dep is not None and vAtss is not None:
            # Add filename, peakamp and areaundercurve, and voltage input to summary table
           
            new_row = {'Filename': file,  'Peak_amplitude(pA)': ssAmp, 'Input_voltage(mV)': vAtss, 'AreaUnderCurve(pA*mV)': areaundercurve_dep}
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    except Exception as e:
        filesnotworking.append(file)
        logging.error(traceback.format_exc())  # log error

# Get summary data for the cell
print(df)  # show the recorded data

print("\nMean of each column:")


mean_b = df['Input_voltage(mV)'].mean()
mean_c = df['AreaUnderCurve(pA*mV)'].mean()
mean_d = df['Peak_Amplitude(pA)'].mean()


print("Mean Input_voltage(mV): " + str(mean_b))
print("Mean area under curve(mV*pA): " + str(mean_c))
print("Mean peak-amplitude(pA): " + str(mean_d))

# Export all the dataframes from all the files analyzed to a single Excel file
# Construct the file name
summary_excelname = os.path.join(save_directory, f"AvgTails_{protocolname}_sweep{swp}.xlsx")

# Use ExcelWriter to save the DataFrame to an Excel file
with pd.ExcelWriter(summary_excelname, engine='xlsxwriter') as writer:
    
    df.to_excel(writer, sheet_name=protocolname, index=False)


# Show files not working
string = ','.join(str(x) for x in filesnotworking)
print("Files not working:" + string)


