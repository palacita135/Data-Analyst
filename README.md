# Data Analyst Workflow Pipeline

A complete, unified workflow for Data Analysis, featuring a Python GUI for ETL (Extract, Transform, Load), automatic MySQL integration, and a dynamic AdminLTE Dashboard.

## 🚀 Features

- **Unified GUI App**: A single interface to manage your workflow.
- **Data Processing**: Upload CSVs and automatically split them into Training/Test sets.
- **Industry-Specific Analysis**: Select your industry (Sales, Logistics, Finance, HR) to generate tailored insights.
- **Auto-SQL Integration**: Automatically creates databases and tables in MySQL and uploads your data.
- **Dynamic Dashboard**: A responsive web dashboard (AdminLTE + Flask) that updates automatically with your latest data.

## 🛠️ Prerequisites

1.  **Python** (3.8 or higher)
2.  **XAMPP** (or any MySQL Server) for the database.
3.  **Web Browser** (Chrome, Edge, etc.)

## 📦 Installation

1.  **Clone/Download** this repository to your computer.
2.  **Install Python Dependencies**:
    Open your terminal/command prompt in the project folder and run:
    ```bash
    pip install -r 3_Python/requirements.txt
    pip install -r 6_Dashboard/requirements.txt
    ```

## ⚡ How to Run

1.  **Start XAMPP**:
    - Open XAMPP Control Panel.
    - Click **Start** next to **MySQL**.

2.  **Run the App**:

    ```bash
    python 3_Python/gui_app.py
    ```

3.  **Use the Workflow**:
    - **Select File**: Choose your raw CSV file.
    - **Select Industry**: Pick the relevant industry (e.g., Sales, Logistics).
    - **MySQL Config**:
      - Default XAMPP settings are pre-filled (`localhost`, `root`, empty password).
      - Just leave them as is if you haven't changed your XAMPP password.
    - **Process**: Click the **"Process & Send to Dashboard"** button.

4.  **View Results**:
    - The app will process your data.
    - It will upload it to your MySQL database.
    - Your web browser will automatically open the **Dashboard** displaying your charts!

## 📂 Directory Structure

- `1_Data`: Store raw and processed data here.
- `2_Excel`: Place for Excel analysis and templates.
- `3_Python`: Contains the **GUI Application** (`gui_app.py`) and analysis scripts.
- `4_MySQL`: SQL schemas and query templates.
- `5_Visualization`: Scripts for generating industry-specific charts.
- `6_Dashboard`: The Flask Web Server and AdminLTE HTML templates.

## 📊 Dashboard

The dashboard is built with **Flask** and **AdminLTE 3**. It uses **Plotly** for interactive charts.

- URL: `http://127.0.0.1:5000` (Opens automatically)
