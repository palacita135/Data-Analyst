-- Sample Queries

-- Select all records
SELECT * FROM sample_data;

-- Calculate average value
SELECT AVG(value) as average_value FROM sample_data;

-- Count records by date
SELECT DATE(created_at) as date, COUNT(*) as count
FROM sample_data
GROUP BY DATE(created_at);
