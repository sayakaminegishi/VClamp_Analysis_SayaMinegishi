''' compare V-clamp files
Used in data where multiple files are created from the same file and with the same protocol in sequence in v-clamp.
Analyzes the properties of the outward and inward currents (tail) in a specified sweep, and compares these properties across different files.
Plots a graph to show the trend with each increasing file number.


'''
import os
import numpy as np
import scipy.optimize
import scipy.signal
import matplotlib.pyplot as plt
import pyabf
import pandas as pd
import traceback
import logging
from PyQt5.QtWidgets import QApplication, QFileDialog
from get_tail_times import getStartEndTail, getDepolarizationStartEnd
from get_tail_times import get_last_sweep_number
from get_protocol_name import get_protocol_name # type: ignore
from getFilePath import get_file_paths, get_only_filename
from apply_low_pass_filter_FUNCTION import low_pass_filter  # type: ignore
from remove_abf_extension import remove_abf_extension
from AvgTailsSameSweep2 import analyze_tail, get_tail_model, monoExp


#select files
app = QApplication([])
options = QFileDialog.Options()
file_paths = get_file_paths() #get the files of interest via an interactive popup window, and sort them in alphabetical order

# Ask protocol type
protocolname = str(input("Enter the protocol type - Henckels, BradleyLong or BradleyShort: "))

#ask sweep number
sweepn = input("Enter the sweep number to analyze (zero-indexed), or enter 'final' for the last sweep: ")
if sweepn == "final":
    sweepnumber = get_last_sweep_number(protocolname)
else:
    sweepnumber = int(sweepn)

#create array to save files not working
filesnotworking = []

# Initialize summary table for recording data
columns = ['Filename', 'Peak_amplitude(pA)', 'Input_voltage_at_peak(mV)','AreaUnderCurve_peak(pA*mV)',  'Tail_amplitude(pA)','Input_voltage_at_trough(mV)','AreaUnderCurve_tail(pA*mV)', 'Tau(sec)']  # column headers


df = pd.DataFrame(columns=columns)  # create an empty dataframe with the specified columns
save_directory = QFileDialog.getExistingDirectory(None, "Select Directory to Save Excel Files", options=options)

#create an array for storing EACH property, where ith element = ith recording in chronological order.
max_amplitudes = [] #max outward current amplitude for this sweep, from each file.
max_tail_amplitudes = [] #lowest current
area_under_curves_tail = [] #area under holding voltage, for the tail region.
tail_durations = [] #duration of the tail current.
tau_vals_tail = [] #tau values of the tail current in each file, for this sweep.


for file in file_paths:
    try:
        ####### GET TRACE AND DENOISE #################

        print("\nWorking on " + file + "\n")

        abfdata = pyabf.ABF(file) #extract raw data
        
        abfdata.setSweep(sweepnumber) #set sweep
    
        # Extract raw sweep data and convert them to arrays
        time = np.array(abfdata.sweepX)
        trace = np.array(abfdata.sweepY)  # Current values. RAW, NOISY DATA
        inputv = np.array(abfdata.sweepC)
        SampleRate = abfdata.dataRate  # sample rate in total samples per second per channel
        baseline = trace[0]

        # Denoise the trace
        denoised_trace = low_pass_filter(trace, SampleRate)
        
        ######### Get TAIL amplitude ############
        # Define start and end times
        startTail, endTail = getStartEndTail(protocolname, sweepnumber) #get tail start and end times

        #analyze region of interest (tail current)
        mask1 = (time >= startTail) & (time <= endTail)
        filtered_values = denoised_trace[mask1]  # trace values, for the hyperpolarizing step
        filtered_time = time[mask1]
        inputv1 = inputv[mask1]

        trough_val = np.min(filtered_values)  #peak current
        index_of_trough = np.argmin(filtered_values) 
        trough_loc = filtered_time[index_of_trough]  + startTail #with respect to the whole trace

        trough_amp = trough_val - baseline
        areaundercurve_tail = np.trapz(filtered_values, filtered_time) #area under the tail curve
        vAtTrough = inputv[index_of_trough] #input voltage at the time of the trough


        ######## GET PEAK CURRENT AMPLITUDE DURING DEPOLARIZATION STEP ###############

        starttime, endtime = getDepolarizationStartEnd(protocolname)
        #analyze region of interest (depolarizing current)
        mask2 = (time >= starttime) & (time <= endtime)
        filtered_values2 = denoised_trace[mask2]  # trace values
        filtered_time2 = time[mask2]
        inputv2 = inputv[mask2]

        peak_val = np.min(filtered_values2)  #peak current
        index_of_pk = np.argmin(filtered_values2) 
        peak_loc = filtered_time2[index_of_pk]  + starttime

        peak_amp = peak_val - baseline
        areaundercurve_peak = np.trapz(filtered_values2, filtered_time2) #area under the  curve
        vAtPeak = inputv2[index_of_pk] #input voltage at the time of the peak

        ############ MORE ON TAIL ANALYSIS ############################################
        ### FIT EXPONENTIAL MODEL TO TAIL CURRENT & GET TAU #############
        a, b, c,tauSec = analyze_tail(time, trace, trough_loc, endTail, SampleRate) #get coefficients for the model. TODO: check
        xtail, ytail= get_tail_model(time, denoised_trace, trough_loc, endTail, SampleRate)

        #plot tail current model
        plt.figure(figsize=(10, 6))
        plt.plot(xtail, ytail, label=f"y = {a:.2f} * exp({b:.2f} * x) + {c:.2f}", color='red')
        plt.xlabel('Time (s)')
        plt.ylabel('Current (pA)')
        plt.title('Exponential Fit: Averaged Line of Best Fit for Sweep ' + str(sweepnumber))
        plt.legend()
        plt.grid(True)
        plt.show()


        ######### ADD V-CLAMP PROPERTIES TO THE SUMMARY TABLE #######################
        if trough_amp is not None and areaundercurve_tail is not None and vAtTrough is not None and peak_amp is not None and areaundercurve_peak is not None and vAtPeak is not None:
            # Add filename, peakamp and areaundercurve, and voltage input to summary table for depolarization and tail current regions
           
            new_row = {
                    'Filename': get_only_filename(file),
                    'Peak_amplitude(pA)': peak_amp, 
                    'Input_voltage_at_peak(mV)': vAtPeak, 
                    'AreaUnderCurve_peak(pA*mV)': areaundercurve_peak,
                    'Tail_amplitude(pA)': trough_amp,
                    'Input_voltage_at_trough(mV)': vAtTrough,
                    'AreaUnderCurve_tail(pA*mV)': areaundercurve_tail,
                    'Tau(sec)': tauSec

                    }
            
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            
    except Exception as e:
        filesnotworking.append(file)
        logging.error(traceback.format_exc())  # log error

# Get summary data 
print(df)  # show the recorded data

# Export all the dataframes from all the files analyzed to a single Excel file
# Construct the file name
summary_excelname = os.path.join(save_directory, f"VclampSummary_{protocolname}_sweep{sweepnumber}.xlsx")

# Use ExcelWriter to save the DataFrame to an Excel file
with pd.ExcelWriter(summary_excelname, engine='xlsxwriter') as writer:
    
    df.to_excel(writer, sheet_name=protocolname, index=False)


# Show files not working
string = ','.join(str(x) for x in filesnotworking)
print("Files not working:" + string)




