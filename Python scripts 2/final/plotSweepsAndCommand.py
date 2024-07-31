'''PLOTS ALL SWEEPS AND COMMAND WAVEFORM OF A GIVEN ABF DATA, STACKED

abf = abf data (after it's imported in main program using abf = pyabf.ABF(file))
base_filename = name of file (used for the title of plot)
save_directory = directory to save output file (defined in the main program)

Created by: Sayaka (Saya) Minegishi with assistance of ChatGPT
Contact: minegishis@brandeis.edu
Date: Jul 21 2024
'''
import pyabf
import matplotlib.pyplot as plt
from savePltAsJpeg import savePltAsJpeg

# Shows a stacked plot of command and recorded traces for all sweeps
def plotAllSweepsAndCommand(abf, base_filename, save_directory):
    fig = plt.figure(figsize=(8, 5))

    # Create subplots
    ax1 = fig.add_subplot(211)
    ax2 = fig.add_subplot(212)

    # Plot recorded data (vclamp) on the first subplot
    for swp in abf.sweepList:
        abf.setSweep(swp)
        ax1.plot(abf.sweepX, abf.sweepY)
    ax1.set_xlabel(abf.sweepLabelX)
    ax1.set_ylabel(abf.sweepLabelY)

    # Plot command (DAC) waveform on the second subplot
    for swp in abf.sweepList:
        abf.setSweep(swp)
        ax2.plot(abf.sweepX, abf.sweepC, 'r')
    ax2.set_xlabel(abf.sweepLabelX)
    ax2.set_ylabel(abf.sweepLabelC)

    # Set the title for the entire figure
    fig.suptitle(base_filename)
    plt.tight_layout()
    plt.subplots_adjust(top=0.9)  # Adjust the top to accommodate the suptitle

    # Uncomment the following line to save the plot as a JPEG file
    # savePltAsJpeg(save_directory, base_filename, plt) 

    # Show the plot
    plt.show()
