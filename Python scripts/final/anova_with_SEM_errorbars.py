'''TWO-WAY ANOVA for  1PBC - with SEM error bars - initial attempt, with errors
current densities WITH PERCENT CHANGE ACROSS TREATMENT GROUPS RELATIVE TO CONTROL FOR EACH STRAIN
Sayaka (Saya) Minegishi
developed with assistance of ChatGPT 

*****
% change in current density for each treatment type with respect to the control current density,
 for each strain independently. Extension of aucAnalysisWKYSHR.py

Assumptions: normality and equal SD <- probably not filled so use Krusal-wallis test


'''


import pandas as pd
import statsmodels.api as sm
from statsmodels.formula.api import ols
from statsmodels.stats.multicomp import pairwise_tukeyhsd
from scipy import stats
import numpy as np 
import matplotlib.pyplot as plt
from scipy.stats import sem


# Path to the Excel file
file_path = '/Users/sayakaminegishi/Documents/Birren Lab/CaCC project/ephys_analysis/areaUnderCurveAllDataSHRWKY copy.xlsx'


df_SHR = pd.read_excel(file_path, sheet_name='SHR')
df_WKY = pd.read_excel(file_path, sheet_name='WKY')


# Ensure all DataFrames have the same columns
all_columns = set(df_SHR.columns).union(set(df_WKY.columns))
df_SHR = df_SHR.reindex(columns=all_columns)
df_WKY = df_WKY.reindex(columns=all_columns)

# Fill missing values with NaN
df_SHR = df_SHR.fillna(pd.NA)
df_WKY = df_WKY.fillna(pd.NA)

print(df_SHR)
# Calculate average current density and standard error of the mean for each treatment and strain
#sem=standard deviation divided by the square root of the number of observations that go into the mean.
#SHR 


currentD_shr_control = df_SHR["Control"] #current densities of SHR individuals in control
print(currentD_shr_control.head()) #works - shows all the current_density values for COntrol group in SHR

currentD_shr_treat = df_SHR["Treatment"] #current densities of SHR individuals in treatment group
currentD_shr_wash = df_SHR["Washout"] #current densities of SHR individuals in washout

# #WKY
currentD_wky_control = df_WKY["Control"] #current densities of WKY individuals in control
currentD_wky_treat = df_WKY["Treatment"] #current densities of SHR individuals in treatment group
currentD_wky_wash = df_WKY["Washout"] #current densities of SHR individuals in washout

#get average current densities
av_currentD_shr_control = currentD_shr_control.mean()
av_currentD_shr_treat = currentD_shr_treat.mean()
av_currentD_shr_wash = currentD_shr_wash.mean()

av_currentD_wky_control = currentD_wky_control.mean()
av_currentD_wky_treat = currentD_wky_treat.mean()
av_currentD_wky_wash = currentD_wky_wash.mean()

#get standard error for each treatment+strain
sem_shr_control = sem(currentD_shr_control)
sem_shr_treat = sem(currentD_shr_treat)
sem_shr_wash = sem(currentD_shr_wash)

sem_wky_control = sem(currentD_wky_control)
sem_wky_treat = sem(currentD_wky_treat)
sem_wky_wash = sem(currentD_wky_wash)

print("sem wky")
print(sem_wky_control)

# # # Create the side-by-side bar plot with custom colors
# plt.figure(figsize=(10, 6))
# plt.rcParams.update({'font.size': 24})


# # #make a barchart of current densities
# # #manual method: #TODO find how to do it with loops

#GRAPH

X = ['Control', 'Treatment (1PBC)', 'Washout'] #define the x axis groups
X_pos = np.arange(len(X)) #tick marks (no. of points) for X axis

SHRId = [av_currentD_shr_control, av_currentD_shr_treat, av_currentD_shr_wash] #in order of X
WKYId = [av_currentD_wky_control, av_currentD_wky_treat, av_currentD_wky_wash] #in order of X
SHR_sem = [sem_shr_control,sem_shr_treat, sem_shr_wash ]
WKY_sem = [sem_wky_control,sem_wky_treat, sem_wky_wash ]


#build the barchart with error bars
fig, ax = plt.subplots()
bar_width = 0.35

ax.bar(X_pos - bar_width/2, SHRId, bar_width, yerr = SHR_sem, align = 'center', alpha = 0.5, ecolor = 'black', capsize = 10, label = 'SHR', color = '#ff2121') #centered at x = X_pos - bar_width/2
ax.bar(X_pos + bar_width/2, WKYId, bar_width, yerr = WKY_sem, align = 'center', alpha = 0.5, ecolor = 'black', capsize = 10, label = 'WKY', color = '#21a3ff') #centered at x = X_pos - bar_width/2

ax.set_ylabel("Current Density (pA/pF)")
ax.set_xticks(X_pos) #markings on the x axis
ax.set_xticklabels(X) #categories corresponding to x ticks
ax.set_title("Average current densities of SHR and WKY at 100mV")

plt.tight_layout()
plt.show()


########### PERCENT CHANGE RELATIVE TO CONTROL - FIND AND GRAPH ###################
# PERCENT OF CONTROL FOR TREAT AND WASH GROUPS, FOR EACH STRAIN, ON AVERAGE
pecentOfControl_treat_SHR =  ((currentD_shr_treat/currentD_shr_control)*100).mean() # if this is x, then there is a 100-x% decrease in SHR_treat relative to control. if >100, say x - 100 % increase
pecentOfControl_wash_SHR = ((currentD_shr_wash/currentD_shr_control)*100).mean()

pecentOfControl_treat_WKY =  ((currentD_wky_treat/currentD_wky_control)*100).mean() # if this is x, then there is a 100-x% decrease in SHR_treat relative to control. if >100, say x - 100 % increase
pecentOfControl_wash_WKY = ((currentD_wky_wash/currentD_wky_control)*100).mean()

# FIND PERCENT decrease relative to control, on average
percent_change_treat_SHR = 100-pecentOfControl_treat_SHR
percent_change_wash_SHR = 100-pecentOfControl_wash_SHR
percent_change_treat_WKY = 100-pecentOfControl_treat_WKY
percent_change_wash_WKY = 100-pecentOfControl_wash_WKY

#find standard error of the percent change
sem_PC_shr_treat = sem((currentD_shr_treat/currentD_shr_control)*100)
sem_PC_shr_wash = sem((currentD_shr_wash/currentD_shr_control)*100)

sem_PC_wky_treat = sem((currentD_wky_treat/currentD_wky_control)*100)
sem_PC_wky_wash = sem((currentD_wky_wash/currentD_wky_control)*100)


categories = ['Treatment (1PBC)', 'Washout'] #define the x axis groups
X_pos = np.arange(len(categories)) #tick marks (no. of points) for X axis

SHR_PC = [percent_change_treat_SHR, percent_change_wash_SHR] #in order of X
WKY_PC = [percent_change_treat_WKY, percent_change_treat_WKY] #in order of X

#group sem's for SHR and WKY using a list
SHR_sem = [sem_PC_shr_treat, sem_PC_shr_wash]
WKY_sem = [sem_PC_shr_treat, sem_PC_shr_wash]



#build the barchart with error bars
fig, ax = plt.subplots()
bar_width = 0.35

ax.bar(X_pos - bar_width/2, SHR_PC, bar_width, yerr = SHR_sem, align = 'center', alpha = 0.5, ecolor = 'black', capsize = 10, label = 'SHR', color = '#ff2121') #centered at x = X_pos - bar_width/2
ax.bar(X_pos + bar_width/2, WKY_PC, bar_width, yerr = WKY_sem, align = 'center', alpha = 0.5, ecolor = 'black', capsize = 10, label = 'WKY', color = '#21a3ff') #centered at x = X_pos - bar_width/2


ax.set_ylabel("Percent change in current density(%)")
ax.set_xticks(X_pos) #markings on the x axis
ax.set_xticklabels(categories) #categories corresponding to x ticks
ax.set_title("Average percent change in current densities of SHR and WKY at 100mV")

plt.tight_layout()
plt.show()






