import pandas as pd

try:
    df = pd.read_csv('7_RAW/portugal_listings_cleaned.csv')
    print(f"Total Rows: {len(df)}")
    
    if 'PublishDate' in df.columns:
        # Convert to datetime
        df['PublishDate'] = pd.to_datetime(df['PublishDate'], errors='coerce')
        
        valid_dates = df['PublishDate'].dropna()
        print(f"Valid Dates: {len(valid_dates)}")
        
        if not valid_dates.empty:
            print(f"Min Date: {valid_dates.min()}")
            print(f"Max Date: {valid_dates.max()}")
            print(f"Date Range: {(valid_dates.max() - valid_dates.min()).days} days")
        else:
            print("No valid dates found in PublishDate column.")
    else:
        print("PublishDate column not found.")
        
except Exception as e:
    print(f"Error: {e}")
