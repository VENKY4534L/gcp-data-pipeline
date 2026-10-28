-- Replace `your-gcp-project-id.your_bigquery_dataset.processed_records`
-- with the fully qualified table created by src/load_bigquery.py.

-- 1. Revenue by region
SELECT
  region,
  ROUND(SUM(amount), 2) AS total_amount,
  COUNT(*) AS record_count
FROM `your-gcp-project-id.your_bigquery_dataset.processed_records`
GROUP BY region
ORDER BY total_amount DESC;

-- 2. Daily trend
SELECT
  event_date,
  ROUND(SUM(amount), 2) AS daily_amount,
  COUNT(*) AS record_count
FROM `your-gcp-project-id.your_bigquery_dataset.processed_records`
GROUP BY event_date
ORDER BY event_date;

-- 3. Largest individual records
SELECT record_id, customer, amount, event_date, region
FROM `your-gcp-project-id.your_bigquery_dataset.processed_records`
ORDER BY amount DESC
LIMIT 10;
