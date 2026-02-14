import pandas as pd
import sys

# Output file for results
output_file = 'analysis_results.txt'

def log(msg):
    print(msg)
    with open(output_file, 'a', encoding='utf-8') as f:
        f.write(msg + '\n')

# Clear previous results
with open(output_file, 'w', encoding='utf-8') as f:
    f.write("=== Portugal Real Estate Analysis (Last 6 Months) ===\n\n")

try:
    # 1. Load Data
    df = pd.read_csv('7_RAW/portugal_listings_cleaned.csv')
    
    # 2. Filter 6 Months
    if 'PublishDate' in df.columns:
        df['PublishDate'] = pd.to_datetime(df['PublishDate'], errors='coerce')
        df = df.dropna(subset=['PublishDate'])
        
        latest_date = df['PublishDate'].max()
        start_date = latest_date - pd.DateOffset(months=6)
        df_6m = df[df['PublishDate'] >= start_date].copy()
        
        log(f"Analysis Period: {start_date.date()} to {latest_date.date()}")
        log(f"Total Listings Analyzed: {len(df_6m)}")
    else:
        log("Error: PublishDate not found.")
        sys.exit()

    log("\n--- 1. Average Price Trend ---")
    df_6m['Month'] = df_6m['PublishDate'].dt.to_period('M')
    trend = df_6m.groupby('Month')['Price'].mean()
    log(trend.to_string())

    log("\n--- 2. Top 5 Districts by Price (ROI Potential) ---")
    district_roi = df_6m.groupby('District')['Price'].mean().sort_values(ascending=False).head(5)
    log(district_roi.to_string())

    log("\n--- 3. Property Type Popularity ---")
    type_pop = df_6m['Type'].value_counts(normalize=True).head(5) * 100
    log(type_pop.to_string())

    log("\n--- 4. Condition Impact (New vs Used) ---")
    if 'Condition' in df_6m.columns:
        cond_price = df_6m.groupby('Condition')['Price'].mean().sort_values()
        log(cond_price.to_string())
    else:
        log("Condition column missing.")

    log("\n--- 5. Luxury Market (Top 10%) ---")
    threshold = df_6m['Price'].quantile(0.90)
    luxury = df_6m[df_6m['Price'] >= threshold]
    log(f"Luxury Threshold: > €{threshold:,.2f}")
    log("Top Luxury Districts:")
    log(luxury['District'].value_counts().head(3).to_string())

    log("\n--- 6. Highest Supply (New Listings) ---")
    supply = df_6m['District'].value_counts().head(5)
    log(supply.to_string())

    log("\n--- 7. Parking Premium ---")
    if 'Parking' in df_6m.columns:
        df_6m['HasParking'] = df_6m['Parking'] > 0
        park_price = df_6m.groupby('HasParking')['Price'].mean()
        if len(park_price) > 1:
            try:
                premium = (park_price[True] - park_price[False]) / park_price[False] * 100
                log(f"Price with Parking: €{park_price[True]:,.2f}")
                log(f"Price without: €{park_price[False]:,.2f}")
                log(f"Premium: {premium:.1f}%")
            except:
                log("Could not calc premium")
        else:
            log("Insufficient data for Parking comparison")

except Exception as e:
    log(f"Error: {e}")
