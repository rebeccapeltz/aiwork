import pandas as pd
import numpy as np
import sanity_check

# 1. Create the "Source of Truth" (Raw Data)
raw_data = {
    'Movie': ['Iron Man', 'The Avengers', 'Endgame', 'Black Widow', 'Thor'],
    'Budget': [140, 220, 356, 200, 150],
    'Global_Box_Office': [585, 1518, 2797, 379, 449],
    'Release_Year': [2008, 2012, 2019, 2021, 2011]
}
raw_df = pd.DataFrame(raw_data)

# 2. Create the "AI-Processed" Data (with Hallucinations)
# Goal: The AI was asked to "Clean the data and calculate a 10% marketing tax"
ai_processed_df = raw_df.copy()

# HALLUCINATION 1: The AI accidentally dropped "Thor" during a filter (Row Count Error)
ai_processed_df = ai_processed_df.iloc[:4] 

# HALLUCINATION 2: The AI "invented" a massive box office for Black Widow (Outlier Error)
ai_processed_df.at[3, 'Global_Box_Office'] = 9999 

# HALLUCINATION 3: The AI calculated 'Budget_With_Tax' but mutated the original 'Budget' 
# column incorrectly (Sum Integrity Error)
ai_processed_df['Budget'] = ai_processed_df['Budget'] * 1.15 

# Displaying the datasets to see the drift
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)

print("--- Raw Data Sample ---")
print(raw_df.head())
print("\n--- AI-Processed Data (With Hallucinations) ---")
print(ai_processed_df.head())

# Now you can run the 'run_dashboard_sanity_checks' function from the previous turn:
report = sanity_check.sanity_check(raw_df, ai_processed_df)
print("\n--- Sanity Check Report ---")
for key, value in report.items():
    if (key == 'sum_integrity') or (key == 'range_integrity'): 
        print(f"{key}:")
        for col, result in value.items():
            print(f"  {col}: {result}")
    else:
        print(f"{key},  {value}")
# print(report)