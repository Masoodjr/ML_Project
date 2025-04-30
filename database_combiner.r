import pandas as pd

# List of your local file paths
file_paths = [
    r'C:\Users\vedan\ML_Project\data_scraping\the_grad_cafe\scraped_profiles_end.xlsx',
    r'C:\Users\vedan\ML_Project\data_scraping\the_grad_cafe\scraped_profiles_in college new code.xlsx',
    r'C:\Users\vedan\ML_Project\data_scraping\the_grad_cafe\scraped_profiles_page_1000_1411.xlsx',
    r'C:\Users\vedan\ML_Project\scraped_profiles.xlsx'
]

# Read all files into a list of DataFrames
dataframes = [pd.read_excel(fp) for fp in file_paths]

# Combine all DataFrames
combined_df = pd.concat(dataframes, ignore_index=True)

# Show the columns to check correct ID column name
print("Columns in the combined dataset:", combined_df.columns.tolist())

# Remove all rows where the ID is duplicated
# (keep only unique IDs, remove all appearances of duplicated IDs)
cleaned_df = combined_df[~combined_df['ID'].duplicated(keep=False)]

# Save the result to a new Excel file
cleaned_df.to_excel(r'C:\Users\vedan\ML_Project\combined_cleaned_profiles.xlsx', index=False)

print("✅ Combination and cleaning complete! File saved as 'combined_cleaned_profiles.xlsx'")
