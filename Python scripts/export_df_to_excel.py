''' EXPORT A DATAFRAME TO EXCEL
This function exports a given dataframe to an excel spreadsheet. 

summary_excelname = name (.xlsx) of output excel file. 
df = dataframe to convert to an excel format
protocolname = name of protocol used.

See Okada Ca Dependence analysis script for example usage.

Created by: Sayaka (Saya) Minegishi
Contact: minegishis@brandeis.edu
Last modified: June 21 2024

'''
import os
import numpy as np
import scipy.optimize
import scipy.signal
import matplotlib.pyplot as plt
import pyabf
import pandas as pd
import traceback
import logging
from PyQt5.QtWidgets import QApplication, QFileDialog
from get_tail_times import getStartEndTail
from get_protocol_name import get_protocol_name # type: ignore
rom getFilePath import get_file_path # type: ignore
from get_tail_times import getStartEndTail
from remove_abf_extension import remove_abf_extension # type: ignore
from getTailCurrentModel import getExpTailModel


#for exporting a single dataframe
def export_single_df_to_excel_(df, summary_excelname, protocolname):
    #get user input
    app = QApplication([])

    # Set the options for the file dialog
    options = QFileDialog.Options() #for displaying file selection options

    # Ask user to select a directory to save the Excel files
    save_directory = QFileDialog.getExistingDirectory(None, "Select Directory to Save Excel Files", options=options)

    if not save_directory:
        print("No directory selected. Exiting...")
        exit()

    print(f"Selected save directory: {save_directory}")
    
    # Use ExcelWriter to save the DataFrame to an Excel file
    with pd.ExcelWriter(summary_excelname, engine='xlsxwriter') as writer:
        
        df.to_excel(writer, sheet_name=protocolname, index=False)


#for exporting a collection of dataferames stored in the array dataframes, where each element of dataframes is a dataframe. 
# Each dataframe in dfarray will be stored in a different spreadsheet of the same workbook.
def export_multiple_df_to_excel_(dataframes, protocolname, file_paths):
    #get user input
    app = QApplication([])

    # Set the options for the file dialog
    options = QFileDialog.Options() #for displaying file selection options

    # Ask user to select a directory to save the Excel files
    save_directory = QFileDialog.getExistingDirectory(None, "Select Directory to Save Excel Files", options=options)

    if not save_directory:
        print("No directory selected. Exiting...")
        exit()

    print(f"Selected save directory: {save_directory}")
    
    # Export all the dataframes from all the files analyzed to a single Excel file
    summary_excelname = summary_excelname = os.path.join(save_directory, "Summary_{protocolname}_All.xlsx") #save to the specified directory
    
    with pd.ExcelWriter(summary_excelname, engine='xlsxwriter') as writer:
        for file, df in zip(file_paths, dataframes):
            file_n = remove_abf_extension(file)
            # Shorten sheetname if necessary
            sheetname = f"Summary_{file_n[:20]}" if len(file_n) > 20 else f"Summary_{file_n}"
            df.to_excel(writer, sheet_name=sheetname, index=False) #export file




