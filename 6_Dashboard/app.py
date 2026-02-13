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
    
    if os.path.exists(data_path):
        with open(data_path, 'r') as f:
            data = json.load(f)
            # Use data from GUI if available
            # For this example, we'll just show a simple chart based on the industry
            industry = data.get("industry", "Unknown")
            
            # Dynamic Chart Generation based on Industry
            if industry == "Sales":
                 df = pd.DataFrame({
                    "Date": ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
                    "Revenue": [100, 120, 110, 140, 130, 160],
                    "Region": ["North", "North", "North", "North", "North", "North"]
                })
                 fig = px.line(df, x="Date", y="Revenue", title=f"{industry} Revenue Trend")
            
            elif industry == "Logistics":
                 df = pd.DataFrame({
                    "Route": ["Route A", "Route B", "Route C"],
                    "Delivery Time": [4, 2, 5],
                    "Status": ["Avg", "Fast", "Slow"]
                })
                 fig = px.bar(df, x="Route", y="Delivery Time", color="Status", title=f"{industry} Delivery Performance")
            
            else:
                 # Default generic chart
                 df = pd.DataFrame({
                    "Category": ["A", "B", "C"],
                    "Values": [10, 20, 30]
                })
                 fig = px.pie(df, values='Values', names='Category', title=f"{industry} Generic Data")

    else:
        # Fallback if no data file (Default to Sales)
        df = pd.DataFrame({
            "Fruit": ["Apples", "Oranges", "Bananas", "Apples", "Oranges", "Bananas"],
            "Amount": [4, 1, 2, 2, 4, 5],
            "City": ["SF", "SF", "SF", "Montreal", "Montreal", "Montreal"]
        })
        fig = px.bar(df, x="Fruit", y="Amount", color="City", barmode="group", title="Default Sales Data")

    # Convert to JSON for the frontend
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template('index.html', graphJSON=graphJSON)

@app.route('/update_data', methods=['POST'])
def update_data():
    # Endpoint to receive data directly from GUI (optional, for real-time updates)
    data = request.json
    # In a real app, you might validate and save this data or trigger a WebSocket update
    print(f"Received update for industry: {data.get('industry')}")
    return jsonify({"status": "success"})

if __name__ == '__main__':
    app.run(debug=True)
