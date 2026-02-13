import plotly
import plotly.express as px
import json
import pandas as pd

def create_sales_chart():
    # Sample Data
    df = pd.DataFrame({
        "Fruit": ["Apples", "Oranges", "Bananas", "Apples", "Oranges", "Bananas"],
        "Amount": [4, 1, 2, 2, 4, 5],
        "City": ["SF", "SF", "SF", "Montreal", "Montreal", "Montreal"]
    })

    # Create Plotly Graph
    fig = px.bar(df, x="Fruit", y="Amount", color="City", barmode="group")
    
    # Convert to JSON
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
