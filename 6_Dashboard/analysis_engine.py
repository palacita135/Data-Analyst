import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import re

class DataAnalyzer:
    def __init__(self, df):
        self.df = df
        self.ensure_types()

    def ensure_types(self):
        """Ensure Date and Numeric columns are correctly typed"""
        if 'Date' in self.df.columns:
            self.df['Date'] = pd.to_datetime(self.df['Date'], errors='coerce')
        
        numeric_cols = ['Net sales', 'Quantity', 'Gross sales', 'Price']
        for col in numeric_cols:
            if col in self.df.columns:
                if self.df[col].dtype == 'object':
                     self.df[col] = self.df[col].astype(str).str.replace(r'[^\d.-]', '', regex=True)
                self.df[col] = pd.to_numeric(self.df[col], errors='coerce').fillna(0)

    def generate_summary(self):
        """Generate text-based insights"""
        summary = {}
        
        # 1. Total Revenue
        if 'Net sales' in self.df.columns:
            total_sales = self.df['Net sales'].sum()
            summary['total_revenue'] = total_sales
        
        # 2. Top Item
        if 'Item' in self.df.columns and 'Quantity' in self.df.columns:
            top_item = self.df.groupby('Item')['Quantity'].sum().idxmax()
            top_qty = self.df.groupby('Item')['Quantity'].sum().max()
            summary['top_item'] = f"{top_item} ({top_qty} sold)"
            
        # 3. Anomaly Detection (Simple Z-Score on Daily Sales)
        if 'Date' in self.df.columns and 'Net sales' in self.df.columns:
            daily = self.df.groupby(self.df['Date'].dt.date)['Net sales'].sum()
            mean = daily.mean()
            std = daily.std()
            if std > 0:
                anomalies = daily[(daily - mean).abs() > 2 * std]
                summary['anomalies'] = len(anomalies)
            else:
                summary['anomalies'] = 0
                
        return summary

    def predict_revenue_next_30_days(self):
        """Simple Linear Regression Forecast"""
        if 'Date' not in self.df.columns or 'Net sales' not in self.df.columns:
            return "Not enough data for prediction."

        try:
            # Aggregate Daily
            daily = self.df.groupby(self.df['Date'].dt.date)['Net sales'].sum().reset_index()
            daily['DayOrdinal'] = pd.to_datetime(daily['Date']).map(pd.Timestamp.toordinal)
            
            if len(daily) < 5:
                # Naive projection if not enough data point
                return daily['Net sales'].mean() * 30

            X = daily[['DayOrdinal']]
            y = daily['Net sales']
            
            model = LinearRegression()
            model.fit(X, y)
            
            # Predict next 30 days
            last_date = daily['Date'].max()
            next_30_days = [last_date + pd.Timedelta(days=i) for i in range(1, 31)]
            next_ordinals = np.array([d.toordinal() for d in next_30_days]).reshape(-1, 1)
            
            predictions = model.predict(next_ordinals)
            total_predicted = predictions.sum()
            
            # Trend description
            slope = model.coef_[0]
            trend = "upward" if slope > 0 else "downward"
            
            return {
                "predicted_total": total_predicted,
                "trend": trend,
                "slope": slope
            }
        except Exception as e:
            return f"Prediction Error: {e}"

    def filter_data(self, period):
        """Filter data based on period (Logic mirrors app.py)"""
        if 'Date' not in self.df.columns: return self.df
        
        df = self.df.copy()
        latest_date = df['Date'].max()
        
        if period == 'daily':
            return df[df['Date'].dt.date == latest_date.date()]
        elif period == 'weekly':
            start_date = latest_date - pd.Timedelta(days=7)
            return df[df['Date'] >= start_date]
        elif period == 'monthly':
            return df[(df['Date'].dt.month == latest_date.month) & (df['Date'].dt.year == latest_date.year)]
        elif period == '3month': # Quarterly
            start_date = latest_date - pd.DateOffset(months=3)
            return df[df['Date'] >= start_date]
        elif period == '6month':
            start_date = latest_date - pd.DateOffset(months=6)
            return df[df['Date'] >= start_date]
        elif period == 'yearly':
            start_date = latest_date - pd.DateOffset(months=12)
            return df[df['Date'] >= start_date]
        return df

    def process_chat_query(self, query):
        """Pattern matching NLP engine"""
        query = query.lower()
        
        # --- 1. Detect Time Period ---
        period = 'all_time'
        period_label = "All Time"
        
        if 'daily' in query or 'today' in query:
            period = 'daily'; period_label = "Daily"
        elif 'weekly' in query or 'week' in query:
            period = 'weekly'; period_label = "Weekly"
        elif 'monthly' in query or 'month' in query:
             period = 'monthly'; period_label = "Monthly"
        elif 'quarterly' in query or 'quarter' in query:
             period = '3month'; period_label = "Quarterly"
        elif 'yearly' in query or 'year' in query:
             period = 'yearly'; period_label = "Yearly"
             
        # Filter DataFrame if a specific period is requested
        df_to_use = self.df
        if period != 'all_time':
             df_to_use = self.filter_data(period)
             if df_to_use.empty:
                 return f"No data available for {period_label} period."
        
        # --- 2. Top Selling / Best Item ---
        # Check for 'top', 'best', etc. AND ('item', 'selling', 'product')
        metric_keywords = ['top', 'best', 'popular', 'highest', 'most']
        subject_keywords = ['item', 'selling', 'product', 'seller']
        
        if any(w in query for w in metric_keywords) and any(s in query for s in subject_keywords):
            if 'Item' in df_to_use.columns and 'Quantity' in df_to_use.columns:
                top = df_to_use.groupby('Item')['Quantity'].sum().nlargest(3)
                if top.empty: return f"No sales found in {period_label}."
                return f"The top selling items ({period_label}) are:\n1. {top.index[0]} ({top.iloc[0]:.0f})\n2. {top.index[1]} ({top.iloc[1]:.0f})\n3. {top.index[2]} ({top.iloc[2]:.0f})"
            return "I need 'Item' and 'Quantity' columns to answer that."

        # --- 3. Total Revenue / Sales ---
        if any(w in query for w in ['revenue', 'sales', 'total', 'income']):
            if 'Net sales' in df_to_use.columns:
                total = df_to_use['Net sales'].sum()
                return f"Total Net Sales ({period_label}) is: Rp {total:,.0f}"

        # --- 4. Prediction (Always uses full history for context, but prediction is forward looking) ---
        if any(w in query for w in ['predict', 'forecast', 'future', 'next month']):
            prediction = self.predict_revenue_next_30_days()
            if isinstance(prediction, dict):
                 return f"Based on historical trends ({prediction['trend']}), I predict the total revenue for the next 30 days will be approx **Rp {prediction['predicted_total']:,.0f}**."
            return str(prediction)

        # --- 5. Count ---
        if 'how many' in query or 'count' in query:
             return f"There are {len(df_to_use)} transactions in ({period_label})."

        return "I can answer questions about: Top Items, Total Revenue, Predictions. Try 'Top selling items daily' or 'Total revenue monthly'."
