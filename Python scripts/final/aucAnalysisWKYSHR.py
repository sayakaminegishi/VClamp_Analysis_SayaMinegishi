'''TWO-WAY ANOVA for  1PBC - current densities
Sayaka (Saya) Minegishi
developed with assistance of ChatGPT 

*****
the two independent variables:
Group1: treatment type - 1PBC, Control, washout
Group 2: strain - wky or shr
measurement: mean current density


Null Hypotheses:
1. there is no difference in the mean of current_density(pA/pF) due to the treatment type
2. There is no difference int he mean of the current_density(pA/pF) due to the strain type
3. There is no interaction effect between the current_density(pA/pF) and the strain type


Assumptions: normality and equal SD <- probably not filled so use Krusal-wallis test


'''


import pandas as pd
import statsmodels.api as sm
from statsmodels.formula.api import ols
from statsmodels.stats.multicomp import pairwise_tukeyhsd
from scipy import stats


# Path to the Excel file
file_path = '/Users/sayakaminegishi/Documents/Birren Lab/CaCC project/ephys_analysis/areaUnderCurveAllDataSHRWKY copy.xlsx'

# Read the Excel file
# df_SHRC = pd.read_excel(file_path, sheet_name='shrControl')
# df_SHRT = pd.read_excel(file_path, sheet_name='shrTreat')
# df_SHRW = pd.read_excel(file_path, sheet_name='shrWash')
# df_WKYC= pd.read_excel(file_path, sheet_name='wkyControl')
# df_WKYT= pd.read_excel(file_path, sheet_name='wkyTreat')
# df_WKYW= pd.read_excel(file_path, sheet_name='wkyWash')

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

# Merge the averages and SEMs into a single DataFrame
avg_current_density['sem'] = sem_current_density['current_density']



# Define custom colors
palette = {"WKY": "#a1deff", "SHR": "#91ffa4"}

# Create the side-by-side bar plot with custom colors
plt.figure(figsize=(10, 6))
sns.barplot(x='Treatment', y='current_density', hue='Strain', data=avg_current_density, palette=palette, ci=True)

# Add labels and title
plt.xlabel('Treatment Type')
plt.ylabel('Average Current Density (pA/pF)')
plt.title('Average Current Density by Treatment Type and Strain, 100mV input')
plt.legend(title='Strain')


# # Overlay individual data points
# sns.stripplot(x='Treatment', y='current_density', hue='Strain', data=df_combined, 
#               dodge=True, palette=palette, alpha=0.6, linewidth=1, jitter=True)

# # Add labels and title
# plt.xlabel('Treatment Type')
# plt.ylabel('Average Current Density (pA/pF)')
# plt.title('Average Current Density by Treatment Type and Strain')
# plt.legend(title='Strain', bbox_to_anchor=(1.05, 1), loc='upper left')

# Show the plot
plt.show()


# Boxplot to visualize the data
sns.boxplot(x='Treatment', y='current_density', hue='Strain', data=df_combined, palette=palette)
plt.title('Boxplot of current_density(pA/pF) by treatment type and strain, 100mV input')
plt.xlabel('Treatment Type')
plt.ylabel('Current Density (pA/pF)')
plt.show()




