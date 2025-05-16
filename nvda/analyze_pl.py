import pandas as pd
import numpy as np
from datetime import datetime

# Read the CSV file - Assuming the GOOGL data file is named 'GOOGL.csv' in the same directory
# User might need to change this if the file name is different
file_path = 'nvda_data/nvda.csv' 
try:
    df = pd.read_csv(file_path)
except FileNotFoundError:
    print(f"错误：无法找到数据文件 '{file_path}'。请确保该文件存在于脚本所在的目录中，或者更新脚本中的 'file_path' 变量。")
    exit()

# Ensure 'P/L' column exists
if 'P/L' not in df.columns:
    print(f"错误：CSV文件中未找到 'P/L' 列。请确保文件 '{file_path}' 包含一个名为 'P/L' 的列，其中包含百分比形式的盈亏数据 (例如 '1.23%')。")
    exit()

# Convert P/L column from string percentage to float
# Handle potential errors if 'P/L' is not in the expected string format
try:
    # Ensure the column is treated as string, remove '%', then convert to numeric
    # Explicitly convert to string first to handle mixed types or NaNs correctly before string operations
    pl_as_str = df['P/L'].astype(str)
    # Replace specific error strings like '#DIV/0!' with empty string before other cleaning
    pl_as_str = pl_as_str.replace(['#DIV/0!', '#N/A', '#VALUE!'], '', regex=False)
    # Replace '%' and strip whitespace
    pl_cleaned = pl_as_str.str.replace('%', '', regex=False).str.strip()
    # Convert to numeric, coercing errors to NaN
    temp_pl_numeric = pd.to_numeric(pl_cleaned, errors='coerce')

    # Check for conversion failures:
    # A conversion failed if an original non-null and non-empty string in 'P/L' is now null in temp_pl_numeric
    # Consider original non-null and non-empty strings as candidates for conversion.
    original_valid_string_mask = df['P/L'].notnull() & (pl_as_str.str.strip() != '')
    conversion_failed_mask = original_valid_string_mask & temp_pl_numeric.isnull()

    if conversion_failed_mask.any():
        # Find the first problematic original value for a more helpful error message
        first_problematic_index = df[conversion_failed_mask].index[0]
        first_problematic_value = df.loc[first_problematic_index, 'P/L']
        print(f"错误：无法将 'P/L' 列中的值 '{first_problematic_value}' (位于行索引 {first_problematic_index}) 转换为数值。请确保所有 'P/L' 值均为纯数字或有效的百分比字符串 (例如 '1.23%')。")
        exit()
    
    df['P/L'] = temp_pl_numeric / 100

except Exception as e: # Catch any other unexpected error during the process
    print(f"处理 'P/L' 列时发生未知错误: {e}")
    exit()
    
# Ensure 'Date' column exists
if 'Date' not in df.columns:
    print(f"错误：CSV文件中未找到 'Date' 列。请确保文件 '{file_path}' 包含一个名为 'Date' 的列，其中包含日期数据。")
    exit()

# Extract year from the date
# Try multiple date formats
def parse_date(date_str):
    for fmt in ('%d-%b-%y', '%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%b %d, %Y'):
        try:
            return pd.to_datetime(date_str, format=fmt)
        except (ValueError, TypeError):
            continue
    raise ValueError(f"无法解析日期：{date_str}。请确保日期格式为 'dd-Mon-yy', 'YYYY-MM-DD', 'MM/DD/YYYY', 'DD/MM/YYYY' 或 'Mon DD, YYYY' 中的一种。")

try:
    df['Date'] = df['Date'].apply(parse_date)
except ValueError as e:
    print(f"日期解析错误: {e}")
    exit()
    
df['Year'] = df['Date'].dt.year

thresholds = sorted([
    0.01,    # 1.0%
    0.015,   # 1.5%
    0.02,    # 2.0%
    0.025,   # 2.5%
    0.03,    # 3.0%
    0.04,    # 4.0%
    0.05,    # 5.0%
    0.0125,  # 1.25%
    0.0175,  # 1.75%
    0.0225   # 2.25%
])

# Create a results dictionary to store counts for each year and threshold
results_positive = {}
results_negative = {}

# Group by year
for year, group in df.groupby('Year'):
    results_positive[year] = {}
    results_negative[year] = {}
    
    # Count days for each threshold
    for threshold_val in thresholds:
        positive_count = (group['P/L'] > threshold_val).sum()
        negative_count = (group['P/L'] < -threshold_val).sum()
        
        results_positive[year][threshold_val] = positive_count
        results_negative[year][threshold_val] = negative_count

# Define column names for the output table
pos_columns = [f'>{t*100:.2f}%'.replace('.00', '') for t in thresholds]
neg_columns = [f'<-{t*100:.2f}%'.replace('.00', '') for t in thresholds]

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
    for i, threshold_val in enumerate(thresholds):
        pos_col_name = pos_columns[i]
        neg_col_name = neg_columns[i]
        
        positive_df.loc[year, pos_col_name] = results_positive[year][threshold_val]
        negative_df.loc[year, neg_col_name] = results_negative[year][threshold_val]

# Add rows for the totals if there's data
if not positive_df.empty:
    positive_df.loc['Total'] = positive_df.sum()
if not negative_df.empty:
    negative_df.loc['Total'] = negative_df.sum()

# Add percentages if there's data
total_days_per_year = df.groupby('Year').size()
if not positive_df.empty and not total_days_per_year.empty:
    for i, threshold_val in enumerate(thresholds):
        pos_col_name = pos_columns[i]
        neg_col_name = neg_columns[i]
        
        for year in sorted(results_positive.keys()):
            if year in total_days_per_year:
                days_in_year = total_days_per_year[year]
                if days_in_year > 0:
                    pos_count = positive_df.loc[year, pos_col_name]
                    neg_count = negative_df.loc[year, neg_col_name]
                    
                    pos_percentage = pos_count / days_in_year * 100
                    neg_percentage = neg_count / days_in_year * 100
                    
                    positive_df.loc[year, pos_col_name] = f"{int(pos_count)} ({pos_percentage:.1f}%)"
                    negative_df.loc[year, neg_col_name] = f"{int(neg_count)} ({neg_percentage:.1f}%)"

# Merge the DataFrames for display
result_df = pd.DataFrame(index=sorted(results_positive.keys()) + ['Total'] if not positive_df.empty else [])

for i, threshold_val in enumerate(thresholds):
    pos_col = pos_columns[i]
    neg_col = neg_columns[i]
    if pos_col in positive_df.columns:
        result_df[pos_col] = positive_df[pos_col]
    if neg_col in negative_df.columns:
        result_df[neg_col] = negative_df[neg_col]

# Handle the 'Total' row for merged DataFrame if it exists
if 'Total' in result_df.index and not positive_df.empty and not negative_df.empty:
    for i, threshold_val in enumerate(thresholds):
        pos_col = pos_columns[i]
        neg_col = neg_columns[i]
        
        pos_totals = []
        neg_totals = []
        
        for year_val in sorted(results_positive.keys()):
            if year_val in positive_df.index and pos_col in positive_df.columns:
                pos_count_str = str(positive_df.loc[year_val, pos_col]).split(' ')[0]
                if pos_count_str.isdigit():
                    pos_totals.append(int(pos_count_str))
            if year_val in negative_df.index and neg_col in negative_df.columns:
                neg_count_str = str(negative_df.loc[year_val, neg_col]).split(' ')[0]
                if neg_count_str.isdigit():
                    neg_totals.append(int(neg_count_str))
        
        if pos_col in result_df.columns:
            result_df.loc['Total', pos_col] = str(sum(pos_totals))
        if neg_col in result_df.columns:
            result_df.loc['Total', neg_col] = str(sum(neg_totals))

# Print the results as a table
if not result_df.empty:
    print("NVDA P/L Analysis:")
    print(result_df.to_string())

    # Export to CSV
    output_csv_path = 'nvda_pl_analysis_directional.csv'
    result_df.to_csv(output_csv_path)
    print(f"\nResults exported to '{output_csv_path}'")
else:
    print("没有足够的数据生成分析报告。")