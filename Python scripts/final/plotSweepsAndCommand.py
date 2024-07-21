'''PLOTS ALL SWEEPS AND COMMAND WAVEFORM OF A GIVEN ABF DATA, STACKED

abf = abf data (after it's imported in main program using abf = pyabf.ABF(file))
base_filename = name of file (used for the title of plot)
save_directory = directory to save output file (defined in the main program)

Created by: Sayaka (Saya) Minegishi
Contact: minegishis@brandeis.edu
Date: Jul 21 2024
'''
import pyabf
import matplotlib.pyplot as plt
from savePltAsJpeg import savePltAsJpeg

#shows a stacked plt of command and recorded traces for all sweeps
def plotAllSweepsAndCommand(abf, base_filename, save_directory):
    fig = plt.figure(figsize = (8,5))

    #plot recorded data (vclamp)
    plt.subplot(211)
    for swp in abf.sweepList:
        plt.plot(abf.sweepX, abf.sweepY)
        plt.xlabel(abf.sweepLabelX)
        plt.ylabel(abf.sweepLabelY)

    # plot command (DAC) waveform
    plt.subplot(212)
    for swp in abf.sweepList:
        plt.plot(abf.sweepX, abf.sweepC, 'r')
        plt.xlabel(abf.sweepLabelX)
        plt.ylabel(abf.sweepLabelC)

    plt.title(base_filename)
    plt.tight_layout()
    #savePltAsJpeg(save_directory, base_filename, plt) #save image as jpeg to the output folder
    plt.show()


