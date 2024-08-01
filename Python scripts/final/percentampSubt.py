'''TWO-WAY ANOVA for  1PBC -  %change in amplitude
Sayaka (Saya) Minegishi
developed with assistance of ChatGPT 

*****
the two independent variables:
Group1: treatment type - 1PBC, Control, washout
Group 2: strain - wky or shr
measurement: mean current density


Null Hypotheses:
1. there is no difference in the mean of %change amplitude due to the treatment type
2. There is no difference int he mean of the current_density(pA/pF) due to the strain type
3. There is no interaction effect between the current_density(pA/pF) and the strain type


Assumptions: normality and equal SD <- probably not filled so use Krusal-wallis test


'''


import pandas as pd
import statsmodels.api as sm
from statsmodels.formula.api import ols
from statsmodels.stats.multicomp import pairwise_tukeyhsd
from scipy import stats
import seaborn as sns
import matplotlib.pyplot as plt





# Path to the Excel file
file_path = '/Users/sayakaminegishi/Documents/Birren Lab/CaCC project/ephys_analysis/areaUnderCurveAllDataSHRWKY copy.xlsx'

# Read the Excel file
# df_SHRC = pd.read_excel(file_path, sheet_name='shrControl')
# df_SHRT = pd.read_excel(file_path, sheet_name='shrTreat')
# df_SHRW = pd.read_excel(file_path, sheet_name='shrWash')
# df_WKYC= pd.read_excel(file_path, sheet_name='wkyControl')
# df_WKYT= pd.read_excel(file_path, sheet_name='wkyTreat')
# df_WKYW= pd.read_excel(file_path, sheet_name='wkyWash')

df_SHR = pd.read_excel(file_path, sheet_name='shrSubt')
df_WKY = pd.read_excel(file_path, sheet_name='wkySubt')


# Ensure all DataFrames have the same columns
all_columns = set(df_SHR.columns).union(set(df_WKY.columns))
df_SHR = df_SHR.reindex(columns=all_columns)
df_WKY = df_WKY.reindex(columns=all_columns)

# Fill missing values with NaN
df_SHR = df_SHR.fillna(pd.NA)
df_WKY = df_WKY.fillna(pd.NA)

# Combine the DataFrames into a single DataFrame suitable for ANOVA
df_SHR = pd.melt(df_SHR.reset_index(), id_vars=['index'], value_vars=['1PBC', 'washout'], var_name='treatment', value_name='PercentChangeAmplitude')
df_SHR['Strain'] = 'SHR'

df_WKY = pd.melt(df_WKY.reset_index(), id_vars=['index'], value_vars=['1PBC', 'washout'], var_name='treatment', value_name='PercentChangeAmplitude')
df_WKY['Strain'] = 'WKY'

# Combine both DataFrames
df_combined = pd.concat([df_SHR, df_WKY], ignore_index=True)

# Rename columns for consistency
df_combined.columns = ['Index', 'Treatment', 'PercentChangeAmplitude', 'Strain']

# Print the combined DataFrame
print(df_combined.head())

############## TWO-WAY ANOVA: IS THERE A DIFFERENCE IN MEAN AMPLITUDE (THE MEASUREMENT) BETWEEN STRAINS, ACROSS TREATMENT GROUPS ############
model = ols('PercentChangeAmplitude ~ C(Treatment) * C(Strain)', data=df_combined).fit()
anova_table = sm.stats.anova_lm(model, typ=2)

print(anova_table)



#### POST HOC TEST - which groups are significant (if any) ###############


# Perform Tukey's HSD test
tukey = pairwise_tukeyhsd(endog=df_combined['PercentChangeAmplitude'], 
                          groups=df_combined['Treatment'] + '-' + df_combined['Strain'],
                          alpha=0.05)

print(tukey)

###### find average for each category

# # Calculate average %change in amp and standard error of the mean for each treatment and strain
# avg_ampChange = df_combined.groupby(['Treatment', 'Strain']).PercentChangeAmplitude.mean().reset_index()
# avg_ampChange = avg_ampChange[avg_ampChange['Treatment']!='control'] #remove rows for control
# sem_ampChange = df_combined.groupby(['Treatment', 'Strain']).PercentChangeAmplitude.sem().reset_index()

# # Merge the averages and SEMs into a single DataFrame
# avg_ampChange['sem'] = sem_ampChange['PercentChangeAmplitude']

# Calculate average %change in amp and standard error of the mean for each treatment and strain
avg_ampChange = df_combined.groupby(['Treatment', 'Strain']).PercentChangeAmplitude.mean().reset_index()
sem_ampChange = df_combined.groupby(['Treatment', 'Strain']).PercentChangeAmplitude.sem().reset_index()

# Merge the averages and SEMs into a single DataFrame
avg_ampChange['sem'] = sem_ampChange['PercentChangeAmplitude']



# Define custom colors
#palette = {"WKY": "#a1deff", "SHR": "#fc3030"}
palette = {"WKY": "#2bdafc", "SHR": "#ff0f0f"}

# Create the side-by-side bar plot with custom colors
plt.figure(figsize=(10, 6))
# setting font sizeto 30
plt.rcParams.update({'font.size': 24})

# x='Treatment'
# y='PercentChangeAmplitude'
# sns.barplot(x='Treatment', y='PercentChangeAmplitude', hue='Strain', data=avg_ampChange, palette=palette, ci=True, order=order)
# yerr1 = avg_ampChange['sem']
# plt.errorbar(x,y,yerr=yerr1, fmt="o", color="black", markersize=8, capsize=20)

# # Add labels and title
# plt.xlabel('Treatment Type')
# plt.ylabel('Percent amplitude change (%)')
# plt.title('Average Percent Change in Current Amplitude by Treatment Type and Strain, 100mV input')
# plt.legend(title='Strain')

# Create the bar plot
ax = sns.barplot(x='Treatment', y='PercentChangeAmplitude', hue='Strain', data=avg_ampChange, palette=palette)
# Calculate the x-coordinates of the bars - ensure error bars are in the center of plot

# Add error bars
# Calculate the x-coordinates of the bars
x_coords = []
for p in ax.patches:
    width = p.get_width()
    x_coords.append(p.get_x() + width / 2)

# Add error bars - make sure y values are aligned
for (i, p), (_, row) in zip(enumerate(ax.patches), avg_ampChange.iterrows()):
    x = p.get_x() + p.get_width() / 2
    y = p.get_height()
    sem = row['sem']
    ax.errorbar(x=x, y=y, yerr=sem, fmt="o", color="black", markersize=8, capsize=20)

# Add labels and title
plt.xlabel('Treatment Type', fontweight = 'bold')
plt.ylabel('Percent amplitude change (%)', fontweight = 'bold')
plt.axhline(y = 100, color = '#15b034', linestyle = '--') 
plt.title('Percent Change in Current Amplitude, 100mV Input', fontsize=24, fontweight = 'bold')
plt.legend(title='Strain')

# Adjust layout to fit title and labels
plt.tight_layout(rect=[0, 0, 1, 0.95])

# Show the plot
plt.legend(title='Strain')



# Show the plot
plt.show()


# # Boxplot to visualize the data
# sns.boxplot(x='Treatment', y='PercentChangeAmplitude', hue='Strain', data=df_combined, palette=palette)
# plt.title('Boxplot of Percent Change in Amplitude by treatment type and strain, 100mV input')
# plt.xlabel('Treatment Type')
# plt.ylabel('Percent amplitude change (%)')
# plt.show()




