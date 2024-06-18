#creates an IV curve from a given abf file
# Script based on SW Harden's, modified by Sayaka (Saya) Minegishi
# June 15 2024

import pyabf
import matplotlib.pyplot as plt
import numpy as np


def createIV2(filename):
    # filename = path to file

    abf = pyabf.ABF(filename)
    pt1 = int(500 * abf.dataPointsPerMs)
    pt2 = int(1000 * abf.dataPointsPerMs)

    currents = []
    voltages = []
    conductances = []

    for sweep in abf.sweepList:
        abf.setSweep(sweep)
        currents.append(np.average(abf.sweepY[pt1:pt2]))
        voltages.append(abf.sweepEpochs.levels[2])
        conductances.append(np.average(abf.sweepY[pt1:pt2]) / abf.sweepEpochs.levels[2])

    # Plot I/V curve
    plt.figure(figsize=(8, 5))
    plt.grid(alpha=.5, ls='--')
    plt.plot(voltages, currents, '.-', ms=15)
    plt.ylabel(abf.sweepLabelY)
    plt.xlabel("Voltage (mV)")
    plt.title(f"I/V Relationship of {abf.abfID}")
    plt.show()

    # Plot Conductance vs Voltage curve
    plt.figure(figsize=(8, 5))
    plt.grid(alpha=.5, ls='--')
    plt.plot(voltages, conductances, '.-', ms=15)
    plt.ylabel("Conductance (nS)")
    plt.xlabel("Voltage (mV)")
    plt.title(f"Conductance/Voltage Relationship of {abf.abfID}")
    plt.show()

    # Return a dictionary with the IV data
    iv_data = {
        "voltages": voltages,
        "currents": currents,
        "conductances": conductances
    }

    return iv_data


####################
    
filename = "/Users/sayakaminegishi/Documents/Birren Lab/CaCC project/DATA_Ephys/2024_06_06_01_0005.abf"
dict = createIV2(filename)