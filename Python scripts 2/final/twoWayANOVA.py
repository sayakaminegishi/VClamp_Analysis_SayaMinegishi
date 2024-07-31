''' Two-Way ANOVA '''

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
import statsmodels.api as sm 
from statsmodels.formula.api import ols
from scipy.stats import levene



def makeInputTableForANOVA(df1C, df1T, df2C, df2T, group1name, group2name, propertyName):
    #eg df1 is a dataframe for control fliles, while df2 contains data for treatment files.
    #propertyName is the column header of the property you're interested in from the df.

    df1C_propertyData = df1C[propertyName] #eg control
    df1T_propertyData= df1T[propertyName] #eg treatment
    df2C_propertyData = df2C[propertyName] #eg control
    df2T_propertyData= df2T[propertyName] #eg treatment


    #combine data into a single df with 3 columns!!! outcome, drug and population,
    dfCombined = pd.DataFrame({
        'Outcome': pd.concat([df1C_propertyData, df1T_propertyData, df2C_propertyData, df2T_propertyData]), 

        'Drug': ['Control'] * len(df1C_propertyData) + ['Treatment'] * len(df1T_propertyData) +
        ['Control'] * len(df2C_propertyData) + ['Treatment'] * len(df2T_propertyData),
        'Population': ['SHR'] * (len(df1C_propertyData)  + len(df1T_propertyData))+
        ['WKY'] * (len(df2C_propertyData) + len(df2T_propertyData))
    })

    print(dfCombined) #view combined df to analyze
    return dfCombined


def conductTwoWayANOVA(dfCombined):
    #fit anova model
    model = ols('Outcome ~ C(Drug)* C(Population)', data = dfCombined).fit()
    anova_table = sm.stats.anova_lm(model, typ=2)
    print(anova_table)


    # Levene's test for homogeneity of variances
    levene_test = levene(dfCombined['Outcome'][dfCombined['Drug'] == 'Control'],
                        dfCombined['Outcome'][dfCombined['Drug'] == 'Treatment'])
    print('Levene’s test:', levene_test)

    # Shapiro-Wilk test for normality
    shapiro_test = stats.shapiro(model.resid)
    print('Shapiro-Wilk test:', shapiro_test)

    return anova_table


######### Population 1 data ########################

showInstructions("Enter name of Population 1")
group1name, ok = QInputDialog.getText(None, "Enter name of Population 1", "Enter name of Population 1: ")

if not ok:
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Warning)
    msg.setText("No text entered. Please enter the name of Population 1.")
    msg.setWindowTitle("Warning")
    msg.exec_()
    exit()

showInstructions("Select control Excel data for Group 1")
options = QFileDialog.Options()

file_pathsC1, _ = QFileDialog.getOpenFileName(None, "Select control excel files for group 1", "", "xlsx Files (*.xlsx);;All Files (*)", options=options)

if not file_pathsC1:
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Warning)
    msg.setText("No file selected. Please select a file.")
    msg.setWindowTitle("Warning")
    msg.exec_()
    exit()

print(f"Selected file: {file_pathsC1}")

controlDf1 = pd.read_excel(file_pathsC1) #convert excel data to a dataframe (pandas)

# Select treatment files
showInstructions("Select treatment files for Group 1")
options = QFileDialog.Options()

file_pathsT1, _ = QFileDialog.getOpenFileNames(None, "Select treatment excel files for group 1", "", "xlsx Files (*.xlsx);;All Files (*)", options=options)

if not file_pathsT1:
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Warning)
    msg.setText("No file selected. Please select a file.")
    msg.setWindowTitle("Warning")
    msg.exec_()
    exit()

print(f"Selected files: {file_pathsT1}")
treatDf1 = pd.read_excel(file_pathsT1)

########POPULATION 2 Data ##############
# Select Population 1 data
showInstructions("Enter name of Group 2")
group2name, ok = QInputDialog.getText(None, "Enter name of Population 2", "Enter name of Population 2: ")

if not ok:
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Warning)
    msg.setText("No text entered. Please enter the name of Population 2.")
    msg.setWindowTitle("Warning")
    msg.exec_()
    exit()

showInstructions("Select control Excel data for Group 2")
options = QFileDialog.Options()

file_pathsC2, _ = QFileDialog.getOpenFileName(None, "Select control excel files for group 2", "", "xlsx Files (*.xlsx);;All Files (*)", options=options)

if not file_pathsC2:
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Warning)
    msg.setText("No file selected. Please select a file.")
    msg.setWindowTitle("Warning")
    msg.exec_()
    exit()

print(f"Selected file: {file_pathsC2}")

controlDf2 = pd.read_excel(file_pathsC2) #convert excel data to a dataframe (pandas)

# Select treatment files
showInstructions("Select treatment files for Group 2")
options = QFileDialog.Options()

file_pathsT2, _ = QFileDialog.getOpenFileNames(None, "Select treatment excel files for group 2", "", "xlsx Files (*.xlsx);;All Files (*)", options=options)

if not file_pathsT2:
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Warning)
    msg.setText("No file selected. Please select a file.")
    msg.setWindowTitle("Warning")
    msg.exec_()
    exit()

print(f"Selected files: {file_pathsT2}")
treatDf2 = pd.read_excel(file_pathsT2)

## Perform ANOVA #########
