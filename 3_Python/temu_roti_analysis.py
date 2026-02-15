import pandas as pd
import os

# Configuration
input_file = r'7_RAW/Temu Roti V2/Raw Data Jun.xlsx'
output_file = r'8_Reports/temu_roti_results.txt'

def log(msg, mode='a'):
    print(msg)
    with open(output_file, mode, encoding='utf-8') as f:
        f.write(msg + '\n')

# Initialize Output
os.makedirs('8_Reports', exist_ok=True)
log("=== Temu Roti Sales Analysis (2024) ===\n", mode='w')

try:
    # 1. Load Data
    xl = pd.ExcelFile(input_file)
    sheet = 'Data Result' if 'Data Result' in xl.sheet_names else xl.sheet_names[0]
    df = pd.read_excel(input_file, sheet_name=sheet)
    
    log(f"Loaded {len(df)} rows from {input_file} (Sheet: {sheet})")

    # 2. Clean Data
    # Dates
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df = df.dropna(subset=['Date'])
        # Filter 2024 for consistency (though file seems to be 2024 only)
        df = df[df['Date'].dt.year == 2024]
        log(f"Date Range: {df['Date'].min().date()} to {df['Date'].max().date()}")
    else:
        log("CRITICAL: 'Date' column not found.")
        exit()

    # Numeric
    numeric_cols = ['Net sales', 'Quantity', 'Gross sales']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # 3. Analysis

    # --- A. Daily Analysis (Day of Week) ---
    log("\n--- A. Daily Analysis (Average Sales by Day) ---")
    df['DayName'] = df['Date'].dt.day_name()
    daily_avg = df.groupby('DayName')['Net sales'].mean().reindex(
        ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    )
    log(daily_avg.to_string())
    best_day = daily_avg.idxmax()
    log(f"Best Performing Day: {best_day} (€{daily_avg.max():,.2f})")

    # --- B. Weekly Analysis ---
    log("\n--- B. Weekly Analysis (Total Sales) ---")
    df['Week'] = df['Date'].dt.isocalendar().week
    weekly_sales = df.groupby('Week')['Net sales'].sum()
    log(weekly_sales.head(5).to_string() + "\n... (showing first 5 weeks)")
    log(f"Average Weekly Sales: €{weekly_sales.mean():,.2f}")

    # --- C. Monthly Analysis ---
    log("\n--- C. Monthly Analysis (Total Sales) ---")
    df['Month'] = df['Date'].dt.to_period('M')
    monthly_sales = df.groupby('Month')['Net sales'].sum()
    log(monthly_sales.to_string())
    
    # --- D. 3-Month (Quarterly) Analysis ---
    log("\n--- D. 3-Month (Quarterly) Analysis ---")
    # Resample requires datetime index
    df_resample = df.set_index('Date')
    quarterly_sales = df_resample['Net sales'].resample('Q').sum()
    log(quarterly_sales.to_string())

    # --- E. 6-Month (Half-Yearly) Analysis ---
    log("\n--- E. 6-Month (Half-Yearly) Analysis ---")
    # Custom grouping: Jan-Jun (H1), Jul-Dec (H2)
    # Offset alias '6M' might not align exactly with calendar half-years without anchor, 
    # so manual grouping is safer for strict calendar half-years.
    df['HalfYear'] = df['Date'].dt.month.apply(lambda x: 'H1 (Jan-Jun)' if x <= 6 else 'H2 (Jul-Dec)')
    half_yearly_sales = df.groupby('HalfYear')['Net sales'].sum()
    log(half_yearly_sales.to_string())

    # --- F. Yearly Analysis ---
    log("\n--- F. Yearly Analysis ---")
    total_sales = df['Net sales'].sum()
    total_qty = df['Quantity'].sum() if 'Quantity' in df.columns else 0
    log(f"Total Revenue (2024): €{total_sales:,.2f}")
    log(f"Total Quantity Sold: {total_qty:,.0f}")
    log(f"Total Transactions: {len(df)}")

    # --- G. Top Items ---
    if 'Item' in df.columns:
        log("\n--- G. Top 5 Items (by Quantity) ---")
        top_items = df.groupby('Item')['Quantity'].sum().sort_values(ascending=False).head(5)
        log(top_items.to_string())

except Exception as e:
    log(f"Error: {e}")
