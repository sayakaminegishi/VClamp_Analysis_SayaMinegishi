'''Percent change after Cd addition'''
import pandas as pd
import statsmodels.api as sm
from statsmodels.formula.api import ols
from statsmodels.stats.multicomp import pairwise_tukeyhsd
from matplotlib import pyplot as plt
import numpy as np

# Path to the Excel file
file_path = '/Users/sayakaminegishi/Documents/Birren Lab/CaCC project/ephys_analysis/bigSummary.xlsx'

# Read the Excel file
df= pd.read_excel(file_path, sheet_name='cadmiumExp')
df = df.dropna() #eliminate NaNs
print(df)


#let control be 100% amplitude

control_sum = sum(df['control'])
control_percent = 100

cd_percent = sum(df['cadmium'])/control_sum *100
washout_percent = sum(df['washout'])/control_sum*100

#SEs from raw data for the error bars
n_control = len(df['control'])
n_cad = len(df['cadmium'])
n_wash = len(df['washout'])

sd_control = np.std(df['control'], ddof=1)
sd_cad = np.std(df['cadmium'], ddof=1)
sd_wash = np.std(df['washout'], ddof=1)

SEc = sd_control / np.sqrt(n_control)
SEcd = sd_cad / np.sqrt(n_cad)
SEw = sd_wash / np.sqrt(n_wash)


# Data for plotting
categories = ['Control', 'Cadmium', 'Washout']
percentages = [control_percent, cd_percent, washout_percent]
errors = [SEc, SEcd, SEw]

# Plotting
fig, ax = plt.subplots(figsize=(10, 7))
plt.rcParams.update({'font.size': 20})
bars = ax.bar(categories, percentages, capsize=10, color='#54e367', edgecolor='#59eb68')

# Adding labels and title
ax.set_ylabel('Percent Change in Current Amplitude (%)', fontweight='bold', fontsize=20)  # Larger font size
ax.set_xlabel('Treatment Type', fontweight='bold', fontsize=20)  # Larger font size
ax.set_title('Percent Change in Current Amplitude After Cd Addition in WKY', 
             fontweight='bold', fontsize=23)  # Adjust the fontsize for title

# Adjust tick parameters
ax.tick_params(axis='both', which='major', labelsize=16)  # Increase tick label size

# Optionally, adjust tick labels font size and rotation
ax.set_xticklabels(categories, fontsize=16)  # Larger font size for x-axis labels
ax.set_yticklabels(ax.get_yticks(), fontsize=16)  # Larger font size for y-axis labels

# Set y-axis limits
ax.set_ylim(0, max(percentages) + 10)  # Adjust y-axis limit to fit error bars

plt.show()

print(percentages)