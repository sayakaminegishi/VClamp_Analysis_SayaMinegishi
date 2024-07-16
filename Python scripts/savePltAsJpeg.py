'''
This function is used to save a plot as a jpeg file.

save_directory = full path to the directory to save the file
imgname = image file name


Created by Sayaka (Saya) Minegishi
minegishis@brandeis.edu
Jul 15 2024
'''

import os

def savePltAsJpeg(save_directory, imgname, plt):
    # Save the plot as a JPEG file
    os.makedirs(save_directory, exist_ok = True) #check that directory exists, create it if doesn't

   
    #FULL PATH to save the image
    save_path = os.path.join(save_directory, imgname)

    # save as jpeg
    plt.savefig(save_path, format = 'jpeg')


