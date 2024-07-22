''' CONCATENATES SELECTED EXCEL TABLES (FILES) VERTICALLY
concatenates excel tables of the same format. store all excel sheets that you want to concatenate 
vertically in a single folder (path).

TODO: fix concatenate_excelTablseFromPath function to match format of the other one!

Created by Sayaka (Saya) Minegishi with assistance from ChatGPT
Contact: minegishis@brandeis.edu
Last modified Jul 22 2024
'''
import pandas as pd
import glob
import numpy as np
import scipy.optimize
import scipy.signal
import matplotlib.pyplot as plt
import pyabf
import traceback
import logging
from PyQt5.QtWidgets import QApplication, QFileDialog, QInputDialog, QMessageBox
import os
from get_base_filename import get_base_filename
from get_tail_times import getDepolarizationStartEnd, getZoomStartEndTimes
from plotSweepsAndCommand import plotAllSweepsAndCommand
from showInstructions import showInstructions


def concatenate_excelTablesFromPath(path):
    # path = the path to the Excel files
    filesnotworking = []


    # Get a list of all Excel files in the directory
    excel_files = glob.glob(path + '*.xlsx')

    # Initialize an empty list to hold DataFrames
    dataframes = []

    # Loop through each file and read it into a DataFrame
    for file in excel_files:
        try:
            df = pd.read_excel(file)
            dataframes.append(df)

        except Exception as e:
            filesnotworking.append(file)
            logging.error(traceback.format_exc())  # log error


    # Concatenate all DataFrames into a single DataFrame
    combined_df = pd.concat(dataframes, ignore_index=True)
    

    # Save the combined DataFrame to a new Excel file 
    combined_df.to_excel('{path}combined_file.xlsx', index=False) #this can be read by statTestsCaCC.py
    # Show files not working
    string = ','.join(str(x) for x in filesnotworking)
    print("Files not working:" + string)

    return combined_df #all the exeel tables concatenated into a single table

#function that takes in an array of excel files

def concatenate_excelTables(excel_files, save_path):
    files_not_working = []

    # Initialize an empty list to hold DataFrames
    dataframes = []

    # Loop through each file and read it into a DataFrame
    for file in excel_files:
        try:
            df = pd.read_excel(file)
            dataframes.append(df)
        except Exception as e:
            files_not_working.append(file)
            logging.error(traceback.format_exc())  # log error

    if dataframes:
        # Concatenate all DataFrames into a single DataFrame
        combined_df = pd.concat(dataframes, ignore_index=True)

        save_path_base = get_base_filename(save_path)
        # Save the combined DataFrame to a new Excel file
        combined_df.to_excel(os.path.join(save_path, f'combined_file_{save_path_base}.xlsx'), index=False)
        # Show files not working
        string = ','.join(str(x) for x in files_not_working)
        if len(files_not_working) == 0:
            string = "None"
        
        print("Files not working:" + string)
        return combined_df  # all the excel tables concatenated into a single table
    else:
        print("No valid Excel files found to concatenate.")
        return None


########### Usage for one set of excel files (i.e. concatenates to make 1 file) ###################

# Give instructions
app = QApplication([])

showInstructions("Select Excel files to concatenate vertically")
options = QFileDialog.Options()
file_paths, _ = QFileDialog.getOpenFileNames(None, "Select Excel files to concatenate vertically", "", "Excel Files (*.xlsx);;All Files (*)", options=options)

print(f"Selected files: {file_paths}")

showInstructions("Select directory to save the concatenated table.")
save_directory = QFileDialog.getExistingDirectory(None, "Select Directory to Save Excel File", options=options)

# Concatenate and print results
concatenatedDf = concatenate_excelTables(file_paths, save_directory)

if concatenatedDf is not None:
    print(concatenatedDf)
else:
    print("No data was concatenated.")
