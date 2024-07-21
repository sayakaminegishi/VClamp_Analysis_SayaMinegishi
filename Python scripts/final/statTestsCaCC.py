''' FUNCTION THAT CONDUCTS STATISTICAL TESTS, GIVEN A DATAFRAME.

 T TESTS FOR CaCC ANALYSIS 

1. COMPARING VCLAMP PEAK AMP 

Note: pip install xlrd and use dataframe1 = pd.read_excel('book2.xlsx') in the main program before 
passing the dataframe as an argument.

Created by: Sayaka(Saya) Minegishi
contact: minegishis@brandeis.edu
Last Modified: Jul 21 2024

'''

from scipy import stats
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import glob


#function to conduct a t test comparing shrdf with wkydf
def conductTtest(shrdf, wkydf, propertyName):
    #shrdf = shr data in dataframe, from compute_peak_amp_DEP.py
    #wkydf = same concept

    #eg. get peak amplitudes from each strain. get data from the property to compare
    shr_propertyData = shrdf[propertyName]
    wky_propertyData= wkydf[propertyName]

    #get average of these data
    shr_avg = shr_propertyData.mean()
    wky_avg = wky_propertyData.mean()
    
    #perform t test comparing propertyName in WKY and SHR
    t_stat, p_val = stats.ttest_ind(shr_propertyData,wky_propertyData)

    #interpret results
    alpha = 0.05

    if p_val < alpha:
        print("Null hypothesis rejected. There is a significant difference in {propertyName} between SHR and WKY")
    else:
        print("Failed to reject the null hypothesis; there is no significant difference in {propertyName} between SHR and WKY")

    return t_stat, p_val



#function to get averages of data and plot comparison 
def getMeansAndSE(shrdf, wkydf, propertyName):
    #shrdf = shr data in dataframe (collection of files, each file = sample (n))
    #wkydf = same concept

    #eg. get peak amplitudes from each strain. get data from the property to compare
    shr_propertyData = shrdf[propertyName]
    wky_propertyData= wkydf[propertyName]

    #get average of these data
    shr_avg = shr_propertyData.mean()
    wky_avg = wky_propertyData.mean()

    # Calculate standard errors => std/sqrt(no. of observations)
    shr_se = shr_propertyData.std() / np.sqrt(len(shr_propertyData))
    wky_se = wky_propertyData.std() / np.sqrt(len(wky_propertyData))

    # Create a DataFrame for plotting
    data = pd.DataFrame({
        'shr_propertyData': shr_propertyData,
        'wky_propertyData': wky_propertyData
    })


    #plot boxplot and standard error
    # Plot the boxplot
    plt.figure(figsize=(10, 6))
    sns.boxplot(data=data)
    plt.title('Boxplot of Property Data')
    plt.ylabel('Values')

    # Add means and standard errors
    means = [shr_avg, wky_avg]
    ses = [shr_se, wky_se]
    categories = ['shr_propertyData', 'wky_propertyData']

    for mean, se, category in zip(means, ses, categories):
        plt.errorbar(category, mean, yerr=se, fmt='o', color='red', capsize=5)

    plt.show()




    return shr_avg, wky_avg, ses


###############
# EXAMPLE USAGE
exceldocSHR = "/Users/sayakaminegishi/Documents/Birren Lab/CaCC project/DATA_Ephys/FOR ANALYSIS/1PBC treatment/SHR cells/SHRN_DIV5_1pbc_7_3/control 7_3_02/PeakAmplitudes_BradleyShort_sweep10.xlsx"
exceldocWKY = "/Users/sayakaminegishi/Documents/Birren Lab/CaCC project/DATA_Ephys/FOR ANALYSIS/1PBC treatment/WKY cells/07_10_02_WKYDIV13_1pbc/1pbc 07_10_02/PeakAmplitudes_BradleyShort_sweep10.xlsx"
propertyName = 'Peak_amplitude(pA)' #example

shrdf = pd.read_excel(exceldocSHR)
wkydf = pd.read_excel(exceldocWKY)

t_stat, p_val = conductTtest(shrdf, wkydf, propertyName)
shr_avg, wky_avg, SEs = getMeansAndSE(shrdf, wkydf, propertyName)

