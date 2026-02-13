import customtkinter as ctk
from tkinter import filedialog
import pandas as pd
import os
import requests
import json
import webbrowser
import threading
import subprocess
import time
import sys
from sklearn.model_selection import train_test_split
from sqlalchemy import create_engine, text

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class ETLApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Data Analyst ETL Tool")
        self.geometry("700x700")

        # Layout configuration
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(7, weight=1) # Adjusted for more rows

        # 1. Title
        self.label_title = ctk.CTkLabel(self, text="Data Analyst ETL Pipeline", font=("Roboto", 24))
        self.label_title.grid(row=0, column=0, padx=20, pady=20)

        # 2. File Selection
        self.btn_file = ctk.CTkButton(self, text="Select CSV File", command=self.select_file)
        self.btn_file.grid(row=1, column=0, padx=20, pady=10)
        self.label_file = ctk.CTkLabel(self, text="No file selected")
        self.label_file.grid(row=2, column=0, padx=20, pady=5)

        # 3. Industry Selection
        self.label_industry = ctk.CTkLabel(self, text="Select Industry:")
        self.label_industry.grid(row=3, column=0, padx=20, pady=(10, 0))
        self.option_industry = ctk.CTkOptionMenu(self, values=["Sales", "Logistics", "Finance", "HR"])
        self.option_industry.grid(row=4, column=0, padx=20, pady=5)

        # 4. Database Configuration (New Section)
        self.frame_db = ctk.CTkFrame(self)
        self.frame_db.grid(row=5, column=0, padx=20, pady=10, sticky="ew")
        self.frame_db.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(self.frame_db, text="MySQL Configuration").grid(row=0, column=0, columnspan=2, pady=5)
        
        ctk.CTkLabel(self.frame_db, text="Host:").grid(row=1, column=0, padx=5, pady=2, sticky="e")
        self.entry_host = ctk.CTkEntry(self.frame_db, placeholder_text="localhost")
        self.entry_host.grid(row=1, column=1, padx=5, pady=2, sticky="ew")
        self.entry_host.insert(0, "localhost")

        ctk.CTkLabel(self.frame_db, text="User:").grid(row=2, column=0, padx=5, pady=2, sticky="e")
        self.entry_user = ctk.CTkEntry(self.frame_db, placeholder_text="root")
        self.entry_user.grid(row=2, column=1, padx=5, pady=2, sticky="ew")
        self.entry_user.insert(0, "root")

        ctk.CTkLabel(self.frame_db, text="Pass:").grid(row=3, column=0, padx=5, pady=2, sticky="e")
        self.entry_pass = ctk.CTkEntry(self.frame_db, show="*")
        self.entry_pass.grid(row=3, column=1, padx=5, pady=2, sticky="ew")

        ctk.CTkLabel(self.frame_db, text="DB Name:").grid(row=4, column=0, padx=5, pady=2, sticky="e")
        self.entry_db = ctk.CTkEntry(self.frame_db, placeholder_text="data_analyst_db")
        self.entry_db.grid(row=4, column=1, padx=5, pady=2, sticky="ew")
        self.entry_db.insert(0, "data_analyst_db")

        # 5. Process Data
        self.btn_process = ctk.CTkButton(self, text="Process & Upload to MySQL", command=self.process_data)
        self.btn_process.grid(row=6, column=0, padx=20, pady=20)
        
        # 6. Log Output
        self.textbox_log = ctk.CTkTextbox(self, width=600, height=150)
        self.textbox_log.grid(row=7, column=0, padx=20, pady=20)

        self.file_path = None
        
        # Start Flask Server in Background
        self.flask_process = None
        self.start_flask_server()

    def log(self, message):
        self.textbox_log.insert("end", message + "\n")
        self.textbox_log.see("end")

    def select_file(self):
        self.file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if self.file_path:
            self.label_file.configure(text=os.path.basename(self.file_path))
            self.log(f"Selected file: {self.file_path}")

    def start_flask_server(self):
        def run_server():
            # Adjust path to your Flask app
            flask_app_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "6_Dashboard", "app.py")
            # Using current python executable
            cmd = [sys.executable, flask_app_path]
            self.flask_process = subprocess.Popen(cmd)
            self.log("Flask Server started in background.")

        thread = threading.Thread(target=run_server, daemon=True)
        thread.start()

    def process_data(self):
        if not self.file_path:
            self.log("Error: No file selected.")
            return

        industry = self.option_industry.get()
        self.log(f"Processing data for Industry: {industry}...")

        try:
            # 1. Load Data
            df = pd.read_csv(self.file_path)
            self.log(f"Loaded {len(df)} rows.")

            # 2. Split Data (Example: 80/20 split)
            train_df, test_df = train_test_split(df, test_size=0.2, random_state=42)
            self.log(f"Split data: {len(train_df)} training, {len(test_df)} testing rows.")
            
            # Save split data (optional)
            output_dir = os.path.join(os.path.dirname(self.file_path), "processed")
            os.makedirs(output_dir, exist_ok=True)
            train_df.to_csv(os.path.join(output_dir, "train.csv"), index=False)
            test_df.to_csv(os.path.join(output_dir, "test.csv"), index=False)
            self.log(f"Saved split files to {output_dir}")

            # 3. Upload to MySQL
            host = self.entry_host.get()
            user = self.entry_user.get()
            password = self.entry_pass.get()
            dbname = self.entry_db.get()
            
            if host and user and dbname:
                try:
                    # Connection String for Server (No DB)
                    server_str = f"mysql+pymysql://{user}:{password}@{host}"
                    server_engine = create_engine(server_str)
                    
                    # Create Database if not exists
                    with server_engine.connect() as conn:
                        conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {dbname}"))
                    
                    self.log(f"Verified Database '{dbname}' exists.")

                    # Connection String for DB
                    db_str = f"mysql+pymysql://{user}:{password}@{host}/{dbname}"
                    engine = create_engine(db_str)
                    
                    self.log(f"Connecting to MySQL: {host}/{dbname}...")
                    
                    # Create table name based on industry (e.g., "sales_data")
                    table_name = f"{industry.lower()}_data"
                    
                    # Write to SQL (replace if exists)
                    df.to_sql(table_name, con=engine, if_exists='replace', index=False)
                    self.log(f"Successfully uploaded data to table '{table_name}' in MySQL!")
                except Exception as db_err:
                    self.log(f"MySQL Error (Skipping upload): {db_err}")
            else:
                 self.log("Skipping MySQL upload (Configuration missing).")

            # 4. Send to Dashboard (Mock API Call / Shared File)
            dashboard_data = {
                "industry": industry,
                "summary": {
                    "total_rows": len(df),
                    "train_rows": len(train_df),
                    "test_rows": len(test_df)
                },
                "sample_data": df.head().to_dict(orient="records")
            }
            
            shared_data_path = "c:/Users/palac/Documents/Data Analyst/6_Dashboard/static/data.json"
            os.makedirs(os.path.dirname(shared_data_path), exist_ok=True)
            with open(shared_data_path, "w") as f:
                json.dump(dashboard_data, f, indent=4)
            
            # Trigger Dashboard Update
            try:
                requests.post("http://127.0.0.1:5000/update_data", json=dashboard_data)
                self.log("Sent update signal to Flask server.")
            except Exception as e:
                self.log(f"Warning: Could not connect to Flask server: {e}")
                
            # Open Browser
            time.sleep(1) 
            webbrowser.open("http://127.0.0.1:5000")
            self.log("Opened Dashboard in Browser.")

        except Exception as e:
            self.log(f"Error: {e}")

    def on_closing(self):
        if self.flask_process:
            self.flask_process.terminate()
        self.destroy()

if __name__ == "__main__":
    app = ETLApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
