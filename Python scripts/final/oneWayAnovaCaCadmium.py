'''For comparing cadmium effects among groups in WKYs. created using assistance from ChatGPT.'''

import pandas as pd
import statsmodels.api as sm
from statsmodels.formula.api import ols
from statsmodels.stats.multicomp import pairwise_tukeyhsd


# Path to the Excel file
file_path = '/Users/sayakaminegishi/Documents/Birren Lab/CaCC project/ephys_analysis/meanAmps.xlsx'

# Read the Excel file
df= pd.read_excel(file_path, sheet_name='CalciumCd')
print(df)

# Melt the DataFrame to make df optimal for anova
df_long = pd.melt(df, var_name='Treatment_Type', value_name='Amplitude') #specify x and y

# Display the transformed DataFrame
print(df_long.head())

########## Fit the ANOVA model to compare differences in Amp betwen treatment types(groups)
model = ols('Amplitude ~ C(Treatment_Type)', data=df_long).fit()
anova_table = sm.stats.anova_lm(model, typ=2)

# Print the ANOVA table
print(anova_table)

## result
#  df = 2.0  F = 5.627951  P = 0.010619 < 0.05, so there is a significant difference among the 3 groups.

######## Post Hoc since significant difference found ###########

# Perform Tukey's HSD test
tukey = pairwise_tukeyhsd(endog=df_long['Amplitude'], groups=df_long['Treatment_Type'], alpha=0.05)

# Print the results
print(tukey)

''' one way ANOVA is significant - that is, at least one group mean (treatmnet type mean) is diffrent from the mean of other groups combined. 
while there is an overall difference among the groups, the post-hoc tests did not find significant pairwise differences between specific groups. 
caused by lack of power due to small sample size.
'''