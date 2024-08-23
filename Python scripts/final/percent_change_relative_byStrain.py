'''TWO-WAY ANOVA for  1PBC - current densities WITH PERCENT CHANGE ACROSS TREATMENT GROUPS RELATIVE TO CONTROL FOR EACH STRAIN
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

# Combine the DataFrames into a single DataFrame suitable for ANOVA
df_SHR = pd.melt(df_SHR.reset_index(), id_vars=['index'], value_vars=['Control', 'Treatment', 'Washout'], var_name='treatment', value_name='current_density')
df_SHR['Strain'] = 'SHR'

df_WKY = pd.melt(df_WKY.reset_index(), id_vars=['index'], value_vars=['Control', 'Treatment', 'Washout'], var_name='treatment', value_name='current_density')
df_WKY['Strain'] = 'WKY'

# Combine both DataFrames
df_combined = pd.concat([df_SHR, df_WKY], ignore_index=True)

# Rename columns for consistency
df_combined.columns = ['Index', 'Treatment', 'current_density', 'Strain']

# Print the combined DataFrame
print(df_combined.head())

############## TWO-WAY ANOVA: IS THERE A DIFFERENCE IN MEAN AMPLITUDE (THE MEASUREMENT) BETWEEN STRAINS, ACROSS TREATMENT GROUPS ############
model = ols('current_density ~ C(Treatment) * C(Strain)', data=df_combined).fit()
anova_table = sm.stats.anova_lm(model, typ=2)

print(anova_table)



#### POST HOC TEST - which groups are significant (if any) ###############
import seaborn as sns
import matplotlib.pyplot as plt


# Perform Tukey's HSD test
tukey = pairwise_tukeyhsd(endog=df_combined['current_density'], 
                          groups=df_combined['Treatment'] + '-' + df_combined['Strain'],
                          alpha=0.05)

print(tukey)

###### find average for each category

# Calculate average current density for each treatment and strain
# avg_current_density = df_combined.groupby(['Treatment', 'Strain']).current_density.mean().reset_index()


# Calculate average current density and standard error of the mean for each treatment and strain
avg_current_density = df_combined.groupby(['Treatment', 'Strain']).current_density.mean().reset_index()
sem_current_density = df_combined.groupby(['Treatment', 'Strain']).current_density.sem().reset_index()

print(avg_current_density)


print(avg_current_density.iloc[0]['current_density'])

#find average current densities and record %change across groups with respect to the control

#avg current densities by inspecting avg_current_density. 
SHRControlID = avg_current_density.iloc[0]['current_density']
SHRTreatID = avg_current_density.iloc[2]['current_density']
SHRWashID = avg_current_density.iloc[4]['current_density']

WKYControlID = avg_current_density.iloc[1]['current_density']
WKYTreatID = avg_current_density.iloc[3]['current_density']
WKYWashID = avg_current_density.iloc[5]['current_density']

######PERCENT CHANGE CALCULATIONS #############

# Define custom colors
#palette = {"WKY": "#a1deff", "SHR": "#fc3d3d"}
palette = {"WKY": "#2bdafc", "SHR": "#ff0f0f"}


# PERCENT OF CONTROL FOR TREAT AND WASH GROUPS, FOR EACH STRAIN
pecentOfControl_treat_SHR =  (SHRTreatID/SHRControlID)*100 # if this is x, then there is a 100-x% decrease in SHR_treat relative to control. if >100, say x - 100 % increase
pecentOfControl_wash_SHR = (SHRWashID/SHRControlID)*100

pecentOfControl_treat_WKY =  (WKYTreatID/WKYControlID)*100 # if this is x, then there is a 100-x% decrease in SHR_treat relative to control. if >100, say x - 100 % increase
pecentOfControl_wash_WKY = (WKYWashID/WKYControlID)*100

# FIND PERCENT decrease
percent_change_treat_SHR = 100-pecentOfControl_treat_SHR
percent_change_wash_SHR = 100-pecentOfControl_wash_SHR
percent_change_treat_WKY = 100-pecentOfControl_treat_WKY
percent_change_wash_WKY = 100-pecentOfControl_wash_WKY


categories = {'SHR_treat', 'SHR_wash', 'WKY_treat', 'WKY_wash'}

percentdata = [['SHR_treat',percent_change_treat_SHR], ['SHR_wash', percent_change_wash_SHR], ['WKY_treat', percent_change_treat_WKY], ['WKY_wash',percent_change_wash_WKY ]]
df_percentchange = pd.DataFrame(percentdata, columns = ['Treatment_Category', 'Percent_change_from_control'])
print(df_percentchange)

#graph percent decrease

# Create the bar plot
ax1 = df_percentchange.plot.bar(x = 'Treatment_Category', y='Percent_change_from_control', rot=0)

#TODO: ASK HOW TO PUT ERROR BARS

# Add labels and title
plt.xlabel('Treatment Type', fontweight="bold")
plt.ylabel('percent change (%)', fontweight="bold")
plt.title('Percent change in current density relative to control at 100mV', fontweight = "bold")



# Merge the averages and SEMs into a single DataFrame
avg_current_density['sem'] = sem_current_density['current_density']


# Create the side-by-side bar plot with custom colors
plt.figure(figsize=(10, 6))
plt.rcParams.update({'font.size': 24})

# Create the bar plot
ax = sns.barplot(x='Treatment', y='current_density', hue='Strain', data=avg_current_density, palette=palette)
# Calculate the x-coordinates of the bars - ensure error bars are in the center of plot
x_coords = []
for p in ax.patches:
    width = p.get_width()
    x_coords.append(p.get_x() + width / 2)

# Add error bars - make sure y values are aligned
for (i, p), (_, row) in zip(enumerate(ax.patches), avg_current_density.iterrows()):
    x = p.get_x() + p.get_width() / 2
    y = p.get_height()
    sem = row['sem']
    ax.errorbar(x=x, y=y, yerr=sem, fmt="o", color="black", markersize=8, capsize=20)

# Add labels and title
plt.xlabel('Treatment Type', fontweight="bold")
plt.ylabel('Average Current Density (pA/pF)', fontweight="bold")
plt.title('Current Density at 100mV', fontweight = "bold")
plt.legend(title='Strain')

# Show the plot
plt.show()





