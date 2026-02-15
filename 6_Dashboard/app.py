from flask import Flask, render_template, request, jsonify, redirect, url_for
import pandas as pd
import json
import plotly
import plotly.express as px
import os

app = Flask(__name__)

@app.route('/')
def index():
    # Load Data from GUI (or use default)
    data_path = os.path.join(app.root_path, 'static', 'data.json')
    
    # Get Period from Request
    period = request.args.get('period', 'monthly')

    # Initialize figures with placeholders (in case of no data)
    fig_trend = px.line(title="Waiting for Data")
    fig_items = px.bar(title="Waiting for Data")
    fig_dining = px.pie(title="Waiting for Data")
    fig_weekly = {} # Initialize empty dict for optional chart
    title = "Sales Trend" # Default title
    
    # --- Recommendation Logic ---
    recommendations = {
        "daily": "Focus on **Sunday**! It's your peak day. Consider a 'Weekend Bundle' to drive volume even higher.",
        "weekly": "Review the **Weekly Trend**. If you see a dip, launch a mid-week flash sale (Wednesday) to stabilize revenue.",
        "monthly": "Capitalize on the **June Spike**. Replicate successful Q2 campaigns in Q4 (October/November) to boost year-end results.",
        "3month": "Quarterly Review: **Q2** is your strongest season. Ensure inventory is maximized for Apr-Jun.",
        "6month": "Half-Yearly Insight: **H1** generates 81% of revenue. Plan aggressive marketing for H2 to balance the year.",
        "yearly": "Yearly Overview: **Es Kopi Susu** is your volume leader. Build your 2025 strategy around Coffee + Food combos."
    }
    recommendation_text = recommendations.get(period, recommendations['monthly'])

    # Helper for formatting currency
    def format_currency(val):
        return f"Rp {val:,.0f}" if val > 1000000 else f"{val:,.0f}"

    def filter_data_by_period(df, period):
        if 'Date' not in df.columns or df.empty:
            return df
        
        # Ensure Date is datetime
        df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce')
        latest_date = df['Date'].max()
        
        if pd.isna(latest_date):
            return df

        if period == 'daily':
            # Strict: LATEST DATE ONLY (1 Day)
            target_date = latest_date.date()
            return df[df['Date'].dt.date == target_date].copy()
            
        elif period == 'weekly':
            # Strict: Last 7 Days (User defined "Weekly" as "One Week")
            start_date = latest_date - pd.Timedelta(days=7)
            return df[df['Date'] >= start_date].copy()
            
        elif period == 'monthly':
            # Strict: Current Month (Calendar Month of Latest Date)
            target_month = latest_date.month
            target_year = latest_date.year
            return df[(df['Date'].dt.month == target_month) & (df['Date'].dt.year == target_year)].copy()

        elif period == '3month':
            # Last 3 Months
            start_date = latest_date - pd.DateOffset(months=3)
            return df[df['Date'] >= start_date].copy()

        elif period == '6month':
            # Last 6 Months
            start_date = latest_date - pd.DateOffset(months=6)
            return df[df['Date'] >= start_date].copy()

        elif period == 'yearly':
            # Last 12 Months (12 Month Data)
            start_date = latest_date - pd.DateOffset(months=12)
            return df[df['Date'] >= start_date].copy()
            
        return df

    if os.path.exists(data_path):
        try:
            with open(data_path, 'r') as f:
                data = json.load(f)
                print(f"DEBUG: Loaded keys from data.json: {data.keys()}") # DEBUG
                
                # Extract sample data (which was converted to string in GUI app)
                sample_data = data.get("sample_data", [])
                
                if sample_data:
                    df = pd.DataFrame(sample_data)
                    
                    # --- Data Type Conversion ---
                    # Convert 'Date' back to datetime
                    if 'Date' in df.columns:
                        df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce')
                        
                    # Convert Numeric columns
                    numeric_cols = ['Net sales', 'Quantity', 'Gross sales', 'Price']
                    for col in numeric_cols:
                        if col in df.columns:
                            # Remove potential currency symbols/commas
                            df[col] = df[col].astype(str).str.replace(',', '', regex=False)
                            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
                    
                    # --- FILTER DATA BASED ON PERIOD ---
                    filtered_df = filter_data_by_period(df, period)
                    
                    # Use filtered_df for all subsequent calculations
                    df = filtered_df 
                    
                    # --- 1. Dynamic Sales Trend based on Period ---
                    if 'Date' in df.columns and 'Net sales' in df.columns:
                        
                        trend_df = pd.DataFrame()
                        x_col = 'Date'
                        
                        if period == 'daily':
                            # 1 Day Data -> Hourly Aggregation
                            # Extract Hour from Date
                            df['Hour'] = df['Date'].dt.hour
                            trend_df = df.groupby('Hour')['Net sales'].sum().reset_index()
                            title = "Daily Sales Trend"
                            x_col = 'Hour'
                            
                        elif period == 'weekly':
                            # 7 Days Data -> Daily Aggregation
                            df['DayDate'] = df['Date'].dt.date
                            trend_df = df.groupby('DayDate')['Net sales'].sum().reset_index()
                            title = "Weekly Sales Trend"
                            x_col = 'DayDate'
                            
                        elif period == 'monthly':
                            # 1 Month Data -> Daily Aggregation
                            df['DayDate'] = df['Date'].dt.date
                            trend_df = df.groupby('DayDate')['Net sales'].sum().reset_index()
                            title = "Monthly Sales Trend"
                            x_col = 'DayDate'

                        elif period == 'yearly':
                             # 1 Year Data -> Monthly Aggregation
                            df['Month'] = df['Date'].dt.to_period('M').astype(str)
                            trend_df = df.groupby('Month')['Net sales'].sum().reset_index()
                            title = "Yearly Sales Trend"
                            x_col = 'Month'

                        else: 
                            # Fallback (3month etc) -> Weekly Aggregation
                            df['Week'] = df['Date'].dt.to_period('W').apply(lambda r: r.start_time)
                            trend_df = df.groupby('Week')['Net sales'].sum().reset_index()
                            if period == '3month': title = "Quarterly Sales Trend"
                            elif period == '6month': title = "Half-Yearly Sales Trend"
                            else: title = "Sales Trend"
                            x_col = 'Week'

                        # Determine Currency Formatting
                        y_fmt = None 
                        if trend_df['Net sales'].max() > 1000000: # Heuristic for Rp
                            title += " (Rp)"
                            fig_trend = px.line(trend_df, x=x_col, y="Net sales", title=title, markers=True)
                            fig_trend.update_yaxes(tickprefix="Rp ", tickformat=".2s")
                        else:
                            fig_trend = px.line(trend_df, x=x_col, y="Net sales", title=title, markers=True)

                    # --- 2. Top Selling Items OR Type Distribution ---
                    if 'Item' in df.columns and 'Quantity' in df.columns:
                        top_items = df.groupby('Item')['Quantity'].sum().reset_index().sort_values(by='Quantity', ascending=False).head(5)
                        fig_items = px.bar(top_items, x="Quantity", y="Item", orientation='h', 
                                         title="Top 5 Items (Qty)", text='Quantity')
                        fig_items.update_layout(yaxis={'categoryorder':'total ascending'})
                    elif 'Type' in df.columns:
                        # Real Estate: Property Type Count
                        type_counts = df['Type'].value_counts().reset_index()
                        type_counts.columns = ['Type', 'Count']
                        fig_items = px.pie(type_counts, names='Type', values='Count', 
                                         title="Property Type Distribution")

                    # --- 3. Dining Option OR Condition OR Avg Sales by Day ---
                    # Logic: Try to produce *some* 3rd chart
                    if 'Dining option' in df.columns:
                         dining_counts = df['Dining option'].value_counts().reset_index()
                         dining_counts.columns = ['Dining Option', 'Count']
                         fig_dining = px.pie(dining_counts, values='Count', names='Dining Option', 
                                           title="Dine In vs Take Away")
                    elif 'Net sales' in df.columns and 'Date' in df.columns:
                         # F&B: Sales by Day of Week (Always useful)
                         if 'Day' not in df.columns: # Check if already created
                             df['Day'] = df['Date'].dt.day_name()
                         day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                         daily_avg = df.groupby('Day')['Net sales'].mean().reindex(day_order).reset_index()
                         
                         fig_dining = px.bar(daily_avg, x='Day', y='Net sales',
                                           title="Avg Sales by Day (Selected Period)", text_auto='.2s')
                         fig_dining.update_yaxes(tickprefix="Rp ", tickformat=".2s")
                    elif 'Condition' in df.columns:
                         # Real Estate: Condition
                         condition_counts = df['Condition'].value_counts().reset_index()
                         condition_counts.columns = ['Condition', 'Count']
                         fig_dining = px.bar(condition_counts, x='Condition', y='Count',
                                           title="Property Condition", text='Count')
                    elif 'Town' in df.columns:
                         # Alternative: Top 10 Towns
                         top_towns = df['Town'].value_counts().head(10).reset_index()
                         top_towns.columns = ['Town', 'Count']
                         fig_dining = px.bar(top_towns, x='Count', y='Town', orientation='h',
                                           title="Top 10 Towns", text='Count')
                         fig_dining.update_layout(yaxis={'categoryorder':'total ascending'})

        except Exception as e:
            print(f"Error processing data: {e}")
            import traceback
            traceback.print_exc()

    # Calculate Totals
    total_orders = len(df) if locals().get('df') is not None and not df.empty else 0
    total_revenue = 0
    if locals().get('df') is not None and not df.empty:
        if 'Net sales' in df.columns:
            total_revenue = df['Net sales'].sum()
        elif 'Price' in df.columns:
             total_revenue = df['Price'].sum()
    
    # Format Currency
    total_revenue_str = format_currency(total_revenue)

    # Convert to JSON
    graph1JSON = json.dumps(fig_trend, cls=plotly.utils.PlotlyJSONEncoder)
    graph2JSON = json.dumps(fig_items, cls=plotly.utils.PlotlyJSONEncoder)
    graph3JSON = json.dumps(fig_dining, cls=plotly.utils.PlotlyJSONEncoder)
    graph4JSON = json.dumps(fig_weekly, cls=plotly.utils.PlotlyJSONEncoder) if fig_weekly else {}

    return render_template('index.html', 
                         graph1JSON=graph1JSON, 
                         graph2JSON=graph2JSON, 
                         graph3JSON=graph3JSON,
                         graph4JSON=graph4JSON,
                         total_orders=total_orders,
                         total_revenue=total_revenue_str,
                         recommendation=recommendation_text,
                         chart1_title=title)

@app.route('/report/<period>')
def report(period):
    return redirect(url_for('index', period=period))


@app.route('/update_data', methods=['POST'])
def update_data():
    # Endpoint to receive data directly from GUI (optional, for real-time updates)
    data = request.json
    # In a real app, you might validate and save this data or trigger a WebSocket update
    print(f"Received update for industry: {data.get('industry')}")
    return jsonify({"status": "success"})

if __name__ == '__main__':
    app.run(debug=True)
