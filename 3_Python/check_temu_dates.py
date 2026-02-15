import pandas as pd
import os

files = [
    r'7_RAW/Temu Roti V2/Raw Data Jun.xlsx',
    r'7_RAW/Temu Roti V2/Raw Data Nov.xlsx'
]

print("Checking Data Ranges...")
all_data = []

for f in files:
    try:
        # Load 'Data Result' sheet (inferred from previous partial output) or first sheet
        xl = pd.ExcelFile(f)
        sheet = 'Data Result' if 'Data Result' in xl.sheet_names else xl.sheet_names[0]
        
        df = pd.read_excel(f, sheet_name=sheet)
        print(f"\nFile: {os.path.basename(f)} (Sheet: {sheet})")
        print(f"Columns: {list(df.columns)}")
        
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
            valid_dates = df['Date'].dropna()
            if not valid_dates.empty:
                print(f"Range: {valid_dates.min().date()} to {valid_dates.max().date()}")
                print(f"Rows: {len(df)}")
                all_data.append(df)
            else:
                print("No valid dates found.")
        else:
            print("'Date' column not found.")
            
    except Exception as e:
        print(f"Error: {e}")

if all_data:
    full_df = pd.concat(all_data, ignore_index=True)
    print("\n--- Combined Data Summary ---")
    print(f"Total Rows: {len(full_df)}")
    print(f"Overall Range: {full_df['Date'].min().date()} to {full_df['Date'].max().date()}")
    
    # Check for months present
    full_df['Month_Year'] = full_df['Date'].dt.to_period('M')
    print("Months Available:")
    print(full_df['Month_Year'].unique())
