''' 
concatenates excel tables of the same format. store all excel sheets that you want to concatenate 
vertically in a single folder (path).

Created by Sayaka (Saya) Minegishi with assistance from ChatGPT
minegishis@brandeis.edu
Jul 21 2024
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


def concatenate_excelTablesFromPath(path):
    # path = the path to the Excel files

    # Get a list of all Excel files in the directory
    excel_files = glob.glob(path + '*.xlsx')

    # Initialize an empty list to hold DataFrames
    dataframes = []

    # Loop through each file and read it into a DataFrame
    for file in excel_files:
        df = pd.read_excel(file)
        dataframes.append(df)

    # Concatenate all DataFrames into a single DataFrame
    combined_df = pd.concat(dataframes, ignore_index=True)

    # Save the combined DataFrame to a new Excel file 
    combined_df.to_excel('{path}combined_file.xlsx', index=False) #this can be read by statTestsCaCC.py

    return combined_df #all the exeel tables concatenated into a single table

#function that takes in an array of excel files
def concatenate_excelTables(excel_files):
    
    # Initialize an empty list to hold DataFrames
    dataframes = []

    # Loop through each file and read it into a DataFrame
    for file in excel_files:
        df = pd.read_excel(file)
        dataframes.append(df)

    # Concatenate all DataFrames into a single DataFrame
    combined_df = pd.concat(dataframes, ignore_index=True)

    # Save the combined DataFrame to a new Excel file 
    combined_df.to_excel('{path}combined_file.xlsx', index=False) #this can be read by statTestsCaCC.py

    return combined_df #all the exeel tables concatenated into a single table


########### example ###################
app = QApplication([])
options = QFileDialog.Options()
file_paths, _ = QFileDialog.getOpenFileNames(None, "Select Excel files to concatenate vertically", "", "ABF Files (*.abf);;All Files (*)", options=options)

print(f"Selected files: {file_paths}")

concatenatedDf = concatenate_excelTables(file_paths)

print(concatenatedDf)