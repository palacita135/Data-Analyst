import pandas as pd
import json
import os

# Paths
input_file = r'C:\Users\palac\Documents\Data Analyst\7_RAW\portugal_listinigs.csv'
output_json = r'C:\Users\palac\Documents\Data Analyst\6_Dashboard\static\data.json'

print(f"Processing {input_file}...")

try:
    # 1. Load Data
    df = pd.read_csv(input_file)
    
    # 2. Clean Data (Real Estate Logic)
    df.drop_duplicates(inplace=True)
    
    if 'Price' in df.columns:
         df['Price'] = pd.to_numeric(df['Price'], errors='coerce')
         df = df.dropna(subset=['Price'])
         df = df[df['Price'] > 0]
    
    if 'District' in df.columns:
        df['District'] = df['District'].astype(str).str.strip().str.title()
        
    cols_to_zero = ['Parking', 'GrossArea', 'TotalArea', 'ConstructionYear', 'Garage', 'Elevator']
    for col in cols_to_zero:
        if col in df.columns:
            df[col] = df[col].fillna(0)
            
    cols_to_unknown = ['EnergyCertificate', 'Condition']
    for col in cols_to_unknown:
        if col in df.columns:
            df[col] = df[col].fillna('Unknown')
            
    # 3. Save to JSON for Dashboard
    # Convert dates to string for JSON serialization
    if 'Date' in df.columns:
        df['Date'] = df['Date'].astype(str)
        
    data_to_save = {
        "sample_data": df.head(5000).to_dict(orient='records'), # Save subset for performance
        "industry": "Real Estate"
    }
    
    os.makedirs(os.path.dirname(output_json), exist_ok=True)
    with open(output_json, 'w') as f:
        json.dump(data_to_save, f)
        
    print(f"Successfully saved {len(df)} rows (subset) to {output_json}")

except Exception as e:
    print(f"Error: {e}")
