'''Get timestamp and create a continuous time array based on those values

firstfile = file that serve as time 0
filepath = file of interest 
'''
import os
import time
from datetime import datetime

def convertToSec(firstfile, filepath):
    #eg filepath = "myfile.abf"

    ######### Creation time of file of interest
    #get time elapsed since EPOCH in float (secs)
    ti_c_foi = os.path.getctime(filepath) #file of interest creatinon time
    
    #convert to timestamp
    c_ti_foi = time.ctime(ti_c_foi)

    print(f"The file of interest was created at {c_ti_foi}.")

    ####### creation time of starting file (time 0 file)
    ti_c_st = os.path.getctime(firstfile) #file of interest creatinon time
    
    c_ti_st = time.ctime(ti_c_st)

    # Convert c_ti_st and c_ti_foi to datetime objects and find difference in seconds
    format_str = "%a %b %d %H:%M:%S %Y"  # Format of the time.ctime() string
    dt_c_ti_foi = datetime.strptime(c_ti_foi, format_str)
    dt_c_ti_st = datetime.strptime(c_ti_st, format_str)

    # Calculate the difference in seconds
    time_difference_seconds = (dt_c_ti_foi - dt_c_ti_st).total_seconds()
    print(f"The time difference in seconds is {time_difference_seconds}.")
    
    return time_difference_seconds #time since start of recording

# createTimeArray() = [0:0.01: finaltime]


        

