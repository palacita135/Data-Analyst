import pandas as pd
import sys

file_path = r"C:\Users\palac\Documents\Data Analyst\7_RAW\Temu Roti V2\November.xlsx"
output_file = "comparison_result.txt"

with open(output_file, "w") as f:
    try:
        xl = pd.ExcelFile(file_path)
        
        f.write("--- RAW DATA SAMPLE ---\n")
        if "Raw Data" in xl.sheet_names:
            df_raw = pd.read_excel(file_path, sheet_name="Raw Data")
            f.write(f"Shape: {df_raw.shape}\n")
            f.write(f"Columns: {df_raw.columns.tolist()}\n")
            f.write(str(df_raw.head().to_string()) + "\n")
        else:
            f.write("'Raw Data' sheet not found.\n")

        f.write("\n--- PROCESSED DATA SAMPLE ('Data' sheet) ---\n")
        if "Data" in xl.sheet_names:
            df_data = pd.read_excel(file_path, sheet_name="Data")
            f.write(f"Shape: {df_data.shape}\n")
            f.write(f"Columns: {df_data.columns.tolist()}\n")
            f.write(str(df_data.head().to_string()) + "\n")

    except Exception as e:
        f.write(f"Error: {e}\n")
