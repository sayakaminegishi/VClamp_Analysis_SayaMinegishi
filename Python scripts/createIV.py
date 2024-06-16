#creates an IV curve from a given abf file
# Script based on SW Harden's, modified by Sayaka (Saya) Minegishi
# June 15 2024

import pyabf
import matplotlib.pyplot as plt
import numpy as np

def createIV(filename):
    #filename = path to file

    abf = pyabf.ABF(filename)
    pt1 = int(500 * abf.dataPointsPerMs)
    pt2 = int(1000 * abf.dataPointsPerMs)

    currents = []
    voltages = []
    for sweep in abf.sweepList:
        abf.setSweep(sweep)
        currents.append(np.average(abf.sweepY[pt1:pt2]))
        voltages.append(abf.sweepEpochs.levels[2])

    plt.figure(figsize=(8, 5))
    plt.grid(alpha=.5, ls='--')
    plt.plot(voltages, currents, '.-', ms=15)
    plt.ylabel(abf.sweepLabelY)
    plt.xlabel(abf.sweepLabelC)
    plt.title(f"I/V Relationship of {abf.abfID}")

    plt.show()
