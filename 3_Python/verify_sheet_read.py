import pandas as pd
import sys

file_path = r"C:\Users\palac\Documents\Data Analyst\7_RAW\Temu Roti V2\November.xlsx"
output_file = "verification_result.txt"

with open(output_file, "w") as f:
    try:
        # 1. Inspect Sheet Names
        xl = pd.ExcelFile(file_path)
        f.write(f"Available Sheets: {xl.sheet_names}\n")

        # 2. Read 'Data' Sheet (Target)
        if "Data" in xl.sheet_names:
            df_data = pd.read_excel(file_path, sheet_name="Data")
            f.write(f"Successfully read 'Data' sheet. Rows: {len(df_data)}\n")
            f.write(str(df_data.head()) + "\n")
        else:
            f.write("Sheet 'Data' not found!\n")

        # 3. Read 'Data Info' Sheet (Old target)
        if "Data Info" in xl.sheet_names:
            df_info = pd.read_excel(file_path, sheet_name="Data Info")
            f.write(f"Successfully read 'Data Info' sheet. Rows: {len(df_info)}\n")
        else:
            f.write("Sheet 'Data Info' not found!\n")

    except Exception as e:
        f.write(f"Error: {e}\n")
