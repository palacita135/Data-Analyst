import pandas as pd

file_path = r"C:\Users\palac\Documents\Data Analyst\7_RAW\Temu Roti V2\November.xlsx"

try:
    xl = pd.ExcelFile(file_path)
    print(f"Sheet names: {xl.sheet_names}")
    
    for sheet in xl.sheet_names:
        print(f"\n--- Sheet: {sheet} ---")
        df = xl.parse(sheet)
        print(df.head())
        print(f"Shape: {df.shape}")

except Exception as e:
    print(f"Error: {e}")
