'''Get timestamp and create a continuous time array based on those values

firstfile = file that serve as time 0
filepath = file of interest
'''
import os
import time

def get_timearray(firstfile, filepath):
    #eg filepath = "myfile.abf"

    ######### Creation time of file of interest
    #get time elapsed since EPOCH in float (secs)
    ti_c_foi = os.path.getctime(filepath) #file of interest creatinon time
    
    #convert to timestamp
    c_ti_foi = time.ctime(ti_c_foi)

    print(f"The file of interest was created at {c_ti_foi}.")

    ####### creation time of starting file (time 0 file)
    

