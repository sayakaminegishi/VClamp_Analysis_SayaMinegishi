''' FUNCTION FORM: FITS AN EXPONENTIAL MODEL FOR THE TAIL CURRENT OF EACH SWEEP, FOR A GIVEN V-CLAMP FILE.
IDENTICAL in functionality to tailcurrentfitting.py, except that this is a function. 
Returns the dataframe with the coefficients (a, b and c) in the exponential model for the specified sweep,
 and the fitted exponential equation for the tail current.


Created by: Sayaka (Saya) Minegishi. Some modifiactions made by ChatGPT.
Contact: minegishis@brandeis.edu
Last modified: June 19 2024

'''
import numpy as np
import scipy.optimize
import matplotlib.pyplot as plt
import pyabf
import pandas as pd
import traceback
import logging
import scipy.signal

from PyQt5.QtWidgets import QApplication, QFileDialog
from get_tail_times import getStartEndTail
from get_protocol_name import get_protocol_name # type: ignore

def getExpTailModel(protocolname, filepath, sweepnumber):
#returns the dataframe containing the coefficients for the exponential model, and the equation of the fitted model.

    ######################################
    # Function to apply low-pass filter
    def low_pass_filter(trace, SampleRate, cutoff=300, order=5):
        nyquist = 0.5 * SampleRate
        normal_cutoff = cutoff / nyquist
        b, a = scipy.signal.butter(order, normal_cutoff, btype='low', analog=False)
        filtered_trace = scipy.signal.filtfilt(b, a, trace)
        return filtered_trace

    # Function to analyze the tail current (from trough to end of tail)
    def analyze_tail(time, trace, trough, HypEnd, sweep, SampleRate):
        def monoExp(x, a, b, c):
            return a * np.exp(b * x) + c
        
        mask = (time >= trough) & (time <= HypEnd)  # region to analyze - from trough to end of tail

        # Fit exponential model to part of tail after trough with initial guess and bounds
        initial_guess = [1, -1, 1]
        bounds = ([-np.inf, -np.inf, -np.inf], [np.inf, 0, np.inf])  # b should be negative for decay

        try:
            params, cv = scipy.optimize.curve_fit(monoExp, time[mask], trace[mask], p0=initial_guess, bounds=bounds, maxfev=10000)
            a, b, c = params
            tauSec = -1 / b  # Tau (time constant)

            # Determine quality of the fit
            squaredDiffs = np.square(trace[mask] - monoExp(time[mask], *params))
            squaredDiffsFromMean = np.square(trace[mask] - np.mean(trace[mask]))
            rSquared = 1 - np.sum(squaredDiffs) / np.sum(squaredDiffsFromMean)
            print(f"R² = {rSquared}")

            # Visualize fitted curve
            plt.scatter(time, trace, label="data")
            x_fit = np.linspace(time[mask].min(), time[mask].max(), 1000)  # x values for line of best fit
            y_fit = monoExp(x_fit, *params)  # y values for fitted curve
            plt.plot(x_fit, y_fit, c="red", label="fit")
            plt.axvline(x=trough, color='b', linestyle='dashed', label='Trough')
            plt.axvline(x=HypEnd, color='b', linestyle='dashed', label='End of hyperpolarization')

            plt.legend()
            plt.show()

            # Inspect the parameters
            print(f"Sweep {sweep}")
            print(f"Y = {a} * exp({b} * x) + {c}")
            print(f"Tau = {tauSec * 1e6} µs")

            return a, b, c
        except RuntimeError as e:
            print(f"Error: {e}")
            return None, None, None

    ########### MAIN PROGRAM ################
    abfdata = pyabf.ABF(filepath)
    num_channels = abfdata.channelCount
    
    # Initialize summary table for recording data
    columns = ['sweep_number', 'a', 'b', 'c', 'tail_amplitude(mV)']  # column headers
    df = pd.DataFrame(columns=columns)  # create an empty dataframe with the specified columns

    try:
        i = sweepnumber
        if num_channels == 1:
                abfdata.setSweep(sweepnumber)
        else:
            abfdata.setSweep(sweepNumber= sweepnumber, channel= 1)

   
        if protocolname == "Okada_tail":
            k = sweepnumber
        else:
            k = 0 #i.e. not okada. 
        
        starttime, endtime = getStartEndTail(protocolname, k) #get tail start and end times


        # Extract sweep data and convert them to arrays
        time = np.array(abfdata.sweepX)
        trace = np.array(abfdata.sweepY)  # Current values
        SampleRate = abfdata.dataRate  # sample rate in total samples per second per channel

        # Denoise the trace
        denoised_trace = low_pass_filter(trace, SampleRate)

        # Get trough
        mask1 = (time >= starttime) & (time <= endtime)
        filtered_values = denoised_trace[mask1]  # trace values, for the hyperpolarizing step
        filtered_time = time[mask1]

        trough_val = np.min(filtered_values)  # minimum value of tail current, in mV
        index_of_min = np.argmin(filtered_values)  # find the index of the minimum value
        trough_loc = filtered_time[index_of_min]  # trough location, in seconds

        baseline = trace[0]  # baseline
        amplitude = trough_val - baseline  # peak negative amplitude, in mV

        afound, bfound, cfound = analyze_tail(time, denoised_trace, trough_loc, endtime, i, SampleRate)
        if afound is not None and bfound is not None and cfound is not None:
            # Add sweep number, a, b, c to the summary table
            afound = round(afound, 3) #round to 3 decimal places
            bfound = round(bfound, 3)
            cfound = round(afound, 3)

            new_row = {'sweep_number': i, 'a': afound, 'b': bfound, 'c': cfound, 'tail_amplitude(mV)': amplitude}
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            df.round(3)
        ############# Get summary data for the cell ################

        # Get summary data
        tailEquation = f"y = {afound} * exp({bfound} * x) + {cfound}"
        print("Recorded fit, y = a * exp(b * x) + c: " + tailEquation)
        print(df)  # show the recorded data

        #plot the fitted exponential curve
        x_values = np.linspace(starttime, endtime, 1000)
        y_values = afound * np.exp(bfound * x_values) + cfound

        plt.figure(figsize=(10, 6))
        plt.plot(x_values, y_values, label=f"y = {afound:.2f} * exp({bfound:.2f} * x) + {cfound:.2f}", color='red')

        # Add labels and title
        plt.xlabel('Time (s)')
        plt.ylabel('Current (pA)')
        plt.title('Exponential fit for tail current')
        plt.legend()
        plt.grid(True)
        plt.show()


    except Exception as e:
        logging.error(traceback.format_exc())  # log error

    return df, tailEquation