from scipy import stats
import numpy as np

"""
    Detect rows with outliers based on Z-score.
    Returns a boolean Series indicating which rows are outliers.
"""

def detect_outliers_zscore(df, columns, threshold=3):
    
    z_scores = np.abs(stats.zscore(df[columns]))
    outlier_rows = (z_scores > threshold).any(axis=1)
    return outlier_rows
