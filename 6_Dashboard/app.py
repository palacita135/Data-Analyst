from flask import Flask, render_template, request, jsonify
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
    
    # Initialize figures with placeholders (in case of no data)
    fig_trend = px.line(title="Waiting for Data")
    fig_items = px.bar(title="Waiting for Data")
    fig_dining = px.pie(title="Waiting for Data")
    
    if os.path.exists(data_path):
        try:
            with open(data_path, 'r') as f:
                data = json.load(f)
                
                # Extract sample data (which was converted to string in GUI app)
                sample_data = data.get("sample_data", [])
                
                if sample_data:
                    df = pd.DataFrame(sample_data)
                    
                    # --- Data Type Conversion ---
                    # Convert 'Date' back to datetime
                    if 'Date' in df.columns:
                        df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce')
                        
                    # Convert Numeric columns (Sales / Real Estate)
                    numeric_cols = ['Net sales', 'Quantity', 'Gross sales', 'Price']
                    for col in numeric_cols:
                        if col in df.columns:
                            # Remove potential currency symbols/commas if any (though usually clean)
                            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
                    
                    # --- 1. Daily Sales Trend OR Price Distribution ---
                    if 'Date' in df.columns and 'Net sales' in df.columns:
                        # Resample/Group by Date (or Day) if needed, but for now plot raw or daily
                        # If multiple entries per day, group by day
                        daily_sales = df.groupby('Date')['Net sales'].sum().reset_index()
                        fig_trend = px.line(daily_sales, x="Date", y="Net sales", 
                                          title="Daily Revenue Trend", markers=True)
                    elif 'Price' in df.columns and 'District' in df.columns:
                         # Real Estate: Average Price by District
                         avg_price = df.groupby('District')['Price'].mean().reset_index().sort_values('Price', ascending=False)
                         fig_trend = px.bar(avg_price, x='District', y='Price', 
                                          title="Average Property Price by District", text_auto='.2s')

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

                    # --- 3. Dining Option OR Condition ---
                    if 'Dining option' in df.columns:
                         dining_counts = df['Dining option'].value_counts().reset_index()
                         dining_counts.columns = ['Dining Option', 'Count']
                         fig_dining = px.pie(dining_counts, values='Count', names='Dining Option', 
                                           title="Dine In vs Take Away")
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
                                           title="Top 10 Towns by Listings", text='Count')
                         fig_dining.update_layout(yaxis={'categoryorder':'total ascending'})
        except Exception as e:
            print(f"Error processing data: {e}")

    # Convert to JSON
    chart_trend = json.dumps(fig_trend, cls=plotly.utils.PlotlyJSONEncoder)
    chart_items = json.dumps(fig_items, cls=plotly.utils.PlotlyJSONEncoder)
    chart_dining = json.dumps(fig_dining, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template('index.html', 
                         chart_trend=chart_trend, 
                         chart_items=chart_items, 
                         chart_dining=chart_dining)

@app.route('/update_data', methods=['POST'])
def update_data():
    # Endpoint to receive data directly from GUI (optional, for real-time updates)
    data = request.json
    # In a real app, you might validate and save this data or trigger a WebSocket update
    print(f"Received update for industry: {data.get('industry')}")
    return jsonify({"status": "success"})

if __name__ == '__main__':
    app.run(debug=True)
