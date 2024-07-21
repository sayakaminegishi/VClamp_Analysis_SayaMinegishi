'''
THIS FUNCTION SAVES A GIVEN PLOT (plt) AS A JPEG FILE

save_directory = full path to the directory to save the file
imgname = image file name

NOTE: call this function before plt.show()

Created by Sayaka (Saya) Minegishi
minegishis@brandeis.edu
Jul 17 2024
'''

import os

def savePltAsJpeg(save_directory, imgname, plt):
    # Save the plot as a JPEG file
    os.makedirs(save_directory, exist_ok = True) #check that directory exists, create it if doesn't

   
    #FULL PATH to save the image
    save_path = os.path.join(save_directory, imgname)

    # save as jpeg
    plt.savefig(save_path, format = 'jpeg')


#test code
import matplotlib.pyplot as plt
import numpy as np
sd='/Users/sayakaminegishi/Documents/Birren Lab/CaCC project'
imname='testplt'
xpoints = np.array([1, 2, 6, 8])
ypoints = np.array([3, 8, 1, 10])

plt.plot(xpoints, ypoints)

#savefig

savePltAsJpeg(sd, imname, plt)

plt.show()