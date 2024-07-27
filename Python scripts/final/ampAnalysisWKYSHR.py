'''TWO-WAY ANOVA for  1PBC
developed with assistance of ChatGPT '''
import pandas as pd
import statsmodels.api as sm
from statsmodels.formula.api import ols


# Path to the Excel file
file_path = '/Users/sayakaminegishi/Documents/Birren Lab/CaCC project/ephys_analysis/meanAmps.xlsx'

# Read the Excel file
df_SHR = pd.read_excel(file_path, sheet_name='SHR')
df_WKY= pd.read_excel(file_path, sheet_name='WKY')

# print(df_WKY.head())
# print(df_SHR.head())

# ########## categorize
# df_SHR_C = df_SHR['CONTROL']
# df_SHR_T = df_SHR['TREAT']
# df_SHR_W = df_SHR['WASH']

# df_WKY_C = df_WKY['control']
# df_WKY_T = df_WKY['treat']
# df_WKY_W = df_WKY['wash']

# Ensure all DataFrames have the same columns
all_columns = set(df_SHR.columns).union(set(df_WKY.columns))
df_SHR = df_SHR.reindex(columns=all_columns)
df_WKY = df_WKY.reindex(columns=all_columns)

# Fill missing values with NaN
df_SHR = df_SHR.fillna(pd.NA)
df_WKY = df_WKY.fillna(pd.NA)

# Combine the DataFrames into a single DataFrame
df_SHR = pd.melt(df_SHR.reset_index(), id_vars=['index'], value_vars=['CONTROL', 'TREAT', 'WASH'], var_name='Group', value_name='Measurement')
df_SHR['Strain'] = 'SHR'

df_WKY = pd.melt(df_WKY.reset_index(), id_vars=['index'], value_vars=['control', 'treat', 'wash'], var_name='Group', value_name='Measurement')
df_WKY['Strain'] = 'WKY'

# Combine both DataFrames
df_combined = pd.concat([df_SHR, df_WKY], ignore_index=True)

# Rename columns for consistency
df_combined.columns = ['Index', 'Group', 'Measurement', 'Strain']

# Print the combined DataFrame
print(df_combined.head())

############## TWO-WAY ANOVA: IS THERE A DIFFERENCE IN MEAN AMPLITUDE (THE MEASUREMENT) BETWEEN STRAINS, ACROSS TREATMENT GROUPS ############
model = ols('Measurement ~ C(Group) * C(Strain)', data=df_combined).fit()
anova_table = sm.stats.anova_lm(model, typ=2)

print(anova_table)

#INTERPRETATION: Since P of C(group) =1.00, which is > 0.05, the group (Control, Treat, wash) has no effect on the peak amplitude.
# P(strain) = 0.22 > 0.5, so no significant difference between strains on the peak amplitude.
#interaction effect: P(group:strain) = 0.018 < 0.05. So the effect of group depends on the effect of the strain. 
#residual sum of squares: 3.078 e+08  - variation in data that is not explained by the model

#### POST HOC TEST - which groups are significant (if any) ###############
import seaborn as sns
import matplotlib.pyplot as plt

# Boxplot to visualize the data
sns.boxplot(x='Group', y='Measurement', hue='Strain', data=df_combined)
plt.title('Boxplot of Measurements by Group and Strain')
plt.show()

from statsmodels.stats.multicomp import pairwise_tukeyhsd

# Perform Tukey's HSD test
tukey = pairwise_tukeyhsd(endog=df_combined['Measurement'], 
                          groups=df_combined['Group'] + '-' + df_combined['Strain'],
                          alpha=0.05)

print(tukey)