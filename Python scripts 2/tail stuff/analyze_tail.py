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

def monoExp(x, a, b, c):
    return a * np.exp(b * x) + c

# Function to analyze the tail current (from trough to end of tail)
def analyze_tail(time, trace, trough, HypEnd, SampleRate):
    

    mask = (time >= trough) & (time <= HypEnd)  # region to analyze - from trough to end of tail

    # Fit exponential model to part of tail after trough with initial guess and bounds
    initial_guess = [1, -1, 1]
    bounds = ([-np.inf, -np.inf, -np.inf], [np.inf, 0, np.inf])  # b should be negative for decay

    try:
        params, cv = scipy.optimize.curve_fit(monoExp, time[mask], trace[mask], p0=initial_guess, bounds=bounds, maxfev=10000)  # Increased maxfev
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
        plt.legend()
        plt.show()

        # Inspect the parameters
        print(f"Y = {a} * exp({b} * x) + {c}")
        print(f"Tau = {tauSec * 1e6} µs")

        return a, b, c, tauSec

    except RuntimeError as e:
        print(f"Error: {e}")
        return None, None, None


def get_tail_model(time, denoised_trace, trough_loc, endtime, SampleRate):
    #starttail = start time of tail, endtail = end time of tail

    try:
        afound, bfound, cfound,tauSec = analyze_tail(time, denoised_trace, trough_loc, endtime, SampleRate)
        if afound is not None and bfound is not None and cfound is not None:
            
            # Print the averaged line of best fit
            print(f"Averaged line of best fit: y = {afound:.3e} * exp({bfound:.2f} * x) + {cfound:.2f}")

            # return resulting curve
            x_values = np.linspace(starttime, endtime, 1000)
            y_values = afound * np.exp(bfound * cfound) + mean_c

            return x_values, y_values

    except Exception as e:
        logging.error(traceback.format_exc())  # log error


