import pandas as pd
import numpy as np
from datetime import datetime

# Read the CSV file
file_path = 'SPX 20240308-20250308.csv'
df = pd.read_csv(file_path)

# Convert P/L column from string percentage to float
df['P/L'] = df['P/L'].str.rstrip('%').astype('float') / 100

# Extract year from the date
df['Date'] = pd.to_datetime(df['Date'], format='%d-%b-%y')
df['Year'] = df['Date'].dt.year

# Define the thresholds
# Using exact decimal values to avoid floating point precision issues
thresholds = [
    0.01,    # 1.0%
    0.0125,  # 1.25%
    0.015,   # 1.5%
    0.0175,  # 1.75%
    0.02,    # 2.0%
    0.0225,  # 2.25%
    0.025,   # 2.5%
    0.03     # 3.0%
]

# Create a results dictionary to store counts for each year and threshold
results_positive = {}
results_negative = {}

# Group by year
for year, group in df.groupby('Year'):
    results_positive[year] = {}
    results_negative[year] = {}
    total_days = len(group)
    
    # Count days for each threshold
    for threshold in thresholds:
        positive_count = (group['P/L'] > threshold).sum()
        negative_count = (group['P/L'] < -threshold).sum()
        
        results_positive[year][threshold] = positive_count
        results_negative[year][threshold] = negative_count

# Define fixed column names to avoid floating point precision issues
pos_columns = [">1.0%", ">1.25%", ">1.5%", ">1.75%", ">2.0%", ">2.25%", ">2.5%", ">3.0%"]
neg_columns = ["<-1.0%", "<-1.25%", "<-1.5%", "<-1.75%", "<-2.0%", "<-2.25%", "<-2.5%", "<-3.0%"]

# Create DataFrames from the results for better display
positive_df = pd.DataFrame(
    index=sorted(results_positive.keys()),
    columns=pos_columns
)

negative_df = pd.DataFrame(
    index=sorted(results_negative.keys()),
    columns=neg_columns
)

# Fill the DataFrames with results
for year in sorted(results_positive.keys()):
    for i, threshold in enumerate(thresholds):
        pos_col_name = pos_columns[i]
        neg_col_name = neg_columns[i]
        
        positive_df.loc[year, pos_col_name] = results_positive[year][threshold]
        negative_df.loc[year, neg_col_name] = results_negative[year][threshold]

# Add rows for the totals
positive_df.loc['Total'] = positive_df.sum()
negative_df.loc['Total'] = negative_df.sum()

# Add percentages
total_days_per_year = df.groupby('Year').size()
for i, threshold in enumerate(thresholds):
    pos_col_name = pos_columns[i]
    neg_col_name = neg_columns[i]
    
    for year in sorted(results_positive.keys()):
        days_in_year = total_days_per_year[year]
        
        pos_count = positive_df.loc[year, pos_col_name]
        neg_count = negative_df.loc[year, neg_col_name]
        
        pos_percentage = pos_count / days_in_year * 100
        neg_percentage = neg_count / days_in_year * 100
        
        positive_df.loc[year, pos_col_name] = f"{int(pos_count)} ({pos_percentage:.1f}%)"
        negative_df.loc[year, neg_col_name] = f"{int(neg_count)} ({neg_percentage:.1f}%)"

# Merge the DataFrames for display
# Create a list of column pairs (positive, negative) for each threshold
column_pairs = []
for threshold in thresholds:
    column_pairs.extend([f">{threshold*100}%", f"<-{threshold*100}%"])

# Create a new merged DataFrame with all columns
result_df = pd.DataFrame(index=sorted(results_positive.keys()))
for i, threshold in enumerate(thresholds):
    pos_col = pos_columns[i]
    neg_col = neg_columns[i]
    result_df[pos_col] = positive_df[pos_col]
    result_df[neg_col] = negative_df[neg_col]

# Add the Total row
result_df.loc['Total'] = pd.Series(dtype='object')
for i, threshold in enumerate(thresholds):
    pos_col = pos_columns[i]
    neg_col = neg_columns[i]
    
    # Extract numeric values
    pos_totals = []
    neg_totals = []
    
    for year in sorted(results_positive.keys()):
        pos_count = int(positive_df.loc[year, pos_col].split(' ')[0])
        neg_count = int(negative_df.loc[year, neg_col].split(' ')[0])
        pos_totals.append(pos_count)
        neg_totals.append(neg_count)
    
    result_df.loc['Total', pos_col] = str(sum(pos_totals))
    result_df.loc['Total', neg_col] = str(sum(neg_totals))

# Print the results as a table
print(result_df.to_string())

# Export to CSV
result_df.to_csv('spx_pl_analysis_directional.csv')
print("\nResults exported to 'spx_pl_analysis_directional.csv'")
