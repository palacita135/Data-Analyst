import pandas as pd
import os

# Define paths
input_file = r'C:\Users\palac\Documents\Data Analyst\7_RAW\portugal_listinigs.csv'
output_file = r'C:\Users\palac\Documents\Data Analyst\7_RAW\portugal_listings_cleaned.csv'

print(f"Reading from: {input_file}")

try:
    df = pd.read_csv(input_file)
    print(f"Initial Shape: {df.shape}")

    # 1. Remove Duplicates
    initial_rows = len(df)
    df.drop_duplicates(inplace=True)
    print(f"Removed {initial_rows - len(df)} duplicates.")

    # 2. Handle Missing Values
    # Drop rows where Price OR District is missing (Critical)
    df.dropna(subset=['Price', 'District'], inplace=True)
    
    # Impute numericals
    cols_to_zero = ['Parking', 'GrossArea', 'TotalArea', 'ConstructionYear', 'Garage', 'Elevator']
    for col in cols_to_zero:
        if col in df.columns:
            df[col] = df[col].fillna(0)
            
    # Impute categorical
    cols_to_unknown = ['EnergyCertificate', 'Condition']
    for col in cols_to_unknown:
        if col in df.columns:
            df[col] = df[col].fillna('Unknown')

    # 3. Data Consistency
    # Ensure Price is positive
    df = df[df['Price'] > 0]
    
    # Text standardization
    text_cols = ['District', 'City', 'Town', 'Type']
    for col in text_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().str.title()

    print(f"Final Shape: {df.shape}")
    
    # 4. Save
    df.to_csv(output_file, index=False)
    print(f"Successfully saved to: {output_file}")

except Exception as e:
    print(f"Error: {e}")
