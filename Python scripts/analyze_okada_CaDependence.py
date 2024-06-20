''' OKADA Ca2+ dependence analysis - AUC & AMP
computes peak amplitude & area under curve for the EACH sweep, where the duration

sweep numbers start from 0.

of depolarization increases with increasing sweep number.

Created by: Sayaka (Saya) Minegishi
Contact: minegishis@brandeis.edu
Last modified: June 19 2024
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
from getFilePath import get_file_path # type: ignore
from get_tail_times import getStartEndTail
from remove_abf_extension import remove_abf_extension # type: ignore
from getTailCurrentModel import getExpTailModel


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

# Ask user to select a directory to save the Excel files
save_directory = QFileDialog.getExistingDirectory(None, "Select Directory to Save Excel Files", options=options)

if not save_directory:
    print("No directory selected. Exiting...")
    exit()

print(f"Selected save directory: {save_directory}")


filesnotworking = []

# Initialize summary table for recording data
columns = ['Filename', 'Sweep_number', 'Peak_amplitude(pA)', 'Input_voltage(mV)','AreaUnderCurve(pA*mV)', 'Fitted_tail_equation']  # column headers

dataframes = []

for file in file_paths:
    file_n = remove_abf_extension(file)
    excelname = file.replace('.abf', '.xlsx')
    
    print("\nWorking on " + file)
    df = pd.DataFrame(columns=columns)  # create an empty dataframe with the specified columns

    abfdata = pyabf.ABF(file)
    num_channels = abfdata.channelCount

    
    peakamps = [] 
    depdurationlist = []    
    areaundercurve_deplist = []   

    for swp in abfdata.sweepList:
        
        try:
            #set channel to analyze - select only the unsubtracted
            if num_channels == 1:
                abfdata.setSweep(swp)
            else:
                abfdata.setSweep(sweepNumber= swp, channel= 1)

            #get duration of depolarization for the sweep (i.e. find endtime)
            #depolarization start time
            starttime, endtime = getStartEndTail("Okada_dep",swp)
            startTail, endTail = getStartEndTail("Okada_tail",swp)

            depDuration = endtime - starttime 
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

            #### analyze tail current - use tail current length that's equal to Henckels
            tailanalysis_df, tailEquation = getExpTailModel("Okada_tail", file, swp)


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
                # Add filename, peakamp, areaundercurve, and voltage input to summary table
                new_row = {
                    'Filename': file_n, 
                    'Sweep_number': swp, 
                    'Peak_amplitude(pA)': peakamp, 
                    'Input_voltage(mV)': vAtPeak, 
                    'AreaUnderCurve(pA*mV)': areaundercurve_dep,
                    'Fitted_tail_equation': tailEquation
                }
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                
        except Exception as e:
            filesnotworking.append(file)
            logging.error(traceback.format_exc())  # log error

    # PLOT RESULTS for this file, for all sweeps - stacked subplot
    fig, axs = plt.subplots(2, 1)
    axs[0].plot(depdurationlist, peakamps)
    axs[0].set_title('Input Voltage Duration(ms) vs. Peak current amplitude(pA) for file ' + file)
    axs[1].plot(depdurationlist, areaundercurve_deplist, 'tab:green')
    axs[1].set_title('Input voltage duration (ms) vs area under curve(pA*ms)')

    for ax in axs.flat:
        ax.set(xlabel='x-label', ylabel='y-label')

    # Hide x labels and tick labels for top plots and y ticks for right plots.
    for ax in axs.flat:
        ax.label_outer()

    # Print summary data for the file
    print(f"Summary for file: {file}")
    print(df)  # show the recorded data for the file
    dataframes.append(df)  # append the dataframe for this file to main dataframe

    
    # Save dataframe to Excel for this file
    try:
        os.makedirs(os.path.dirname(excelname), exist_ok=True)  # ensure directory exists
        df.to_excel(excelname, index=False)
    except OSError as e:
        logging.error(f"Error saving {excelname}: {e}")



# Export all the dataframes from all the files analyzed to a single Excel file
summary_excelname = summary_excelname = os.path.join(save_directory, "Summary_Okada_All.xlsx") #save to the specified directory
with pd.ExcelWriter(summary_excelname, engine='xlsxwriter') as writer:
    for file, df in zip(file_paths, dataframes):
        file_n = remove_abf_extension(file)
        # Shorten sheetname if necessary
        sheetname = f"Summary_{file_n[:20]}" if len(file_n) > 20 else f"Summary_{file_n}"
        df.to_excel(writer, sheet_name=sheetname, index=False)

# Show files not working
if filesnotworking:
    string = ', '.join(filesnotworking)
    print("Files not working: " + string)

