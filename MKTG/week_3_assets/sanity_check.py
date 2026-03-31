import pandas as pd
import numpy as np

def sanity_check(raw_df, processed_df):
    results = {}

    # 1. Row Count Validation
    results['row_consistency'] = len(raw_df) == len(processed_df)
    results['row_count_diff'] = len(raw_df) - len(processed_df)

    # 2. Null Value Impact
    # AI often misinterprets nulls. Check if null counts changed unexpectedly.
    results['nulls_in_raw'] = raw_df.isnull().sum().sum()
    results['nulls_in_processed'] = processed_df.isnull().sum().sum()

    # 3. Summation Integrity (Critical for Financial Dashboards)
    # Check if the total of a numeric column matches after AI processing
    numeric_cols = raw_df.select_dtypes(include=[np.number]).columns
    sum_checks = {}
    for col in numeric_cols:
        if col in processed_df.columns:
            diff = abs(raw_df[col].sum() - processed_df[col].sum())
            sum_checks[col] = "Pass" if diff < 1e-6 else f"Fail (Diff: {diff})"
    results['sum_integrity'] = sum_checks

    # 4. Range Validation (Detecting Hallucinated Outliers)
    # Check if processed data min/max exceeds raw data bounds
    range_checks = {}
    for col in numeric_cols:
        if col in processed_df.columns:
            oob_max = processed_df[col].max() > raw_df[col].max()
            oob_min = processed_df[col].min() < raw_df[col].min()
            range_checks[col] = "Safe" if not (oob_max or oob_min) else "Out of Bounds"
    results['range_integrity'] = range_checks

  
    return results

# Example Usage:
# report = sanity_check(my_original_csv, my_ai_transformed_df)
# print(report)