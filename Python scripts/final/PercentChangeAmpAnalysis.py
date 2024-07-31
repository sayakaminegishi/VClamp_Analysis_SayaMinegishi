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

df_SHR = pd.read_excel(file_path, sheet_name='SHRChangePts')
df_WKY = pd.read_excel(file_path, sheet_name='WKYChangePts')


# Ensure all DataFrames have the same columns
all_columns = set(df_SHR.columns).union(set(df_WKY.columns))
df_SHR = df_SHR.reindex(columns=all_columns)
df_WKY = df_WKY.reindex(columns=all_columns)

# Fill missing values with NaN
df_SHR = df_SHR.fillna(pd.NA)
df_WKY = df_WKY.fillna(pd.NA)

# Combine the DataFrames into a single DataFrame suitable for ANOVA
df_SHR = pd.melt(df_SHR.reset_index(), id_vars=['index'], value_vars=['control', '1PBC', 'washout'], var_name='treatment', value_name='PercentChangeAmplitude')
df_SHR['Strain'] = 'SHR'

df_WKY = pd.melt(df_WKY.reset_index(), id_vars=['index'], value_vars=['control', '1PBC', 'washout'], var_name='treatment', value_name='PercentChangeAmplitude')
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

# Calculate average %change in amp and standard error of the mean for each treatment and strain
avg_ampChange = df_combined.groupby(['Treatment', 'Strain']).PercentChangeAmplitude.mean().reset_index()
sem_ampChange = df_combined.groupby(['Treatment', 'Strain']).PercentChangeAmplitude.sem().reset_index()

# Merge the averages and SEMs into a single DataFrame
avg_ampChange['sem'] = sem_ampChange['PercentChangeAmplitude']



# Define custom colors
palette = {"WKY": "#a1deff", "SHR": "#adc3f7"}

# Create the side-by-side bar plot with custom colors
plt.figure(figsize=(10, 6))
order = ['control', '1PBC', 'washout']

sns.barplot(x='Treatment', y='PercentChangeAmplitude', hue='Strain', data=avg_ampChange, palette=palette, ci=True, order=order)

# Add labels and title
plt.xlabel('Treatment Type')
plt.ylabel('Percent amplitude change (%)')
plt.title('Average Percent Change in Current Amplitude by Treatment Type and Strain, 100mV input')
plt.legend(title='Strain')



# Show the plot
plt.show()


# Boxplot to visualize the data
sns.boxplot(x='Treatment', y='PercentChangeAmplitude', hue='Strain', data=df_combined, palette=palette)
plt.title('Boxplot of Percent Change in Amplitude by treatment type and strain, 100mV input')
plt.xlabel('Treatment Type')
plt.ylabel('Percent amplitude change (%)')
plt.show()




