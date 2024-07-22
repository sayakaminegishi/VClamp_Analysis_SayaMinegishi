''' Mann-whitney test '''

from scipy import stats
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
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
from concatenate_excelTables import concatenate_excelTables
from scipy.stats import mannwhitneyu


def conductMWtest(df1, df2, propertyName):
    #eg df1 is a dataframe for control fliles, while df2 contains data for treatment files.
    #propertyName is the column header of the property you're interested in from the df.

    g1_propertyData = df1[propertyName] #eg control
    g2_propertyData= df2[propertyName] #eg treatment

    Uval, p = mannwhitneyu(g1_propertyData, g2_propertyData, method="exact") #Reports statistic for g1. exact test statistic, not asymptotic, since small sample size.
    print(f"U = {Uval}") #print test statistic
    print(f"p-value= {p}")

    return Uval, p



######### FOR ONE STRAIN - comparing 1PBC group with control #################
# Select Control files
showInstructions("Select control Excel data (concatenated table)")
options = QFileDialog.Options()

file_pathsC, _ = QFileDialog.getOpenFileName(None, "Select control excel files", "", "xlsx Files (*.xlsx);;All Files (*)", options=options)

if not file_pathsC:
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Warning)
    msg.setText("No file selected. Please select a file.")
    msg.setWindowTitle("Warning")
    msg.exec_()
    exit()

print(f"Selected file: {file_pathsC}")

controlDf = pd.read_excel(file_pathsC)

# Select treatment files
showInstructions("Select treatment (1PBC) files for the same strain")
options = QFileDialog.Options()

file_pathsT2, _ = QFileDialog.getOpenFileNames(None, "Select treatment excel files", "", "xlsx Files (*.xlsx);;All Files (*)", options=options)

if not file_pathsT2:
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Warning)
    msg.setText("No file selected. Please select a file.")
    msg.setWindowTitle("Warning")
    msg.exec_()
    exit()

print(f"Selected files: {file_pathsT2}")
treatDf = pd.read_excel(file_pathsT2)




########### comparing SHR vs WKY 1PBC group


##### ccomparing two strains but with the control group

##### comparing the SEs?