'''remove outliers
threshold_z = zscore threshold for defining outliers
Sayaka Minegishi'''
from scipy import stats
import numpy as np

def removeOutliersNormalized(data, threshold_z):
    z = np.abs(stats.zscore(data)) #find z score from given y-values
    print(z)

    outlier_indices = np.where(z > threshold_z)[0]
    no_outliers = np.delete(data, outlier_indices)
   

    return no_outliers


   