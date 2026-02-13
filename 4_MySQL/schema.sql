-- Schema for Data Analyst Workflow

CREATE DATABASE IF NOT EXISTS data_analyst_db;
USE data_analyst_db;

-- Example Table
CREATE TABLE IF NOT EXISTS sample_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    value DECIMAL(10, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
