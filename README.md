# GCP Data Pipeline – Data Ingestion and ETL Processing

A portfolio-ready starter project demonstrating a staged ETL workflow with Python, Google Cloud Storage (GCS), Pub/Sub, and BigQuery.

## Architecture

1. **Ingestion** – a CSV file is placed in a GCS bucket.
2. **Event notification** – a Pub/Sub message identifies the uploaded object.
3. **Transformation** – Python validates and cleans records.
4. **Analytics storage** – transformed rows are loaded into BigQuery.
5. **Analysis** – SQL queries summarize the processed dataset.

> **Important:** This repository is a starter implementation. The local CSV transformation and unit tests can run without a GCP account. GCS, Pub/Sub, and BigQuery integrations require a Google Cloud project, enabled APIs, IAM permissions, and configuration. Do not claim the cloud workflow is deployed until you have configured and tested it in your own GCP project.

## Repository structure

```text
gcp-data-pipeline/
├── data/sample_data.csv
├── src/
│   ├── ingest.py
│   ├── transform.py
│   └── load_bigquery.py
├── sql/analytics_queries.sql
├── tests/test_transform.py
├── requirements.txt
├── config.example.json
├── .env.example
├── .gitignore
└── README.md
```

## 1. Requirements

- Python 3.10+
- Git (for GitHub upload)
- Optional: Google Cloud project with billing enabled, and `gcloud` CLI for cloud integration

## 2. Run locally in VS Code

Open this folder in VS Code. In **Terminal → New Terminal**, create and activate a virtual environment.

### Windows PowerShell

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python src/transform.py --input data/sample_data.csv --output data/processed_data.csv
python -m unittest discover -s tests -v
```

If PowerShell blocks activation, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` in that terminal, then activate again. You can also install packages with `.venv\Scripts\python.exe -m pip install -r requirements.txt` without activating the environment.

## 3. Optional GCP setup

1. Create or select a Google Cloud project.
2. Enable **Cloud Storage**, **Pub/Sub**, and **BigQuery** APIs.
3. Create a GCS bucket and a Pub/Sub topic.
4. Configure IAM with least-privilege permissions for the identity running the pipeline.
5. Create a BigQuery dataset and destination table.
6. Authenticate locally with `gcloud auth application-default login`, or use an approved workload identity in a deployed environment.
7. Set the environment variables described below.

### Environment variables

- `GCP_PROJECT_ID`: your Google Cloud project ID.
- `GCS_BUCKET`: bucket for raw CSV files.
- `PUBSUB_TOPIC`: topic name for upload notifications (optional).
- `BIGQUERY_DATASET`: destination dataset name.
- `BIGQUERY_TABLE`: destination table name.

Never commit service-account keys, `.env` files, tokens, or passwords.

## 4. Upload a CSV to GCS and publish an event

After setting `GCP_PROJECT_ID`, `GCS_BUCKET`, and optionally `PUBSUB_TOPIC`:

```powershell
python src/ingest.py --file data/sample_data.csv --upload-to-gcs --publish-event
```

The script uploads the CSV to GCS. If `--publish-event` is supplied, it publishes a JSON message containing the bucket and object name to Pub/Sub. This script publishes an event directly; it does not automatically configure a GCS-to-Pub/Sub notification subscription. For an automatic event-driven deployment, configure a Cloud Storage notification or Eventarc trigger separately.

## 5. Transform data

```powershell
python src/transform.py --input data/sample_data.csv --output data/processed_data.csv
```

The transformation normalizes column names, trims text, parses dates, validates required fields, and removes duplicate records. Invalid records are excluded with a warning.

## 6. Load to BigQuery

```powershell
python src/load_bigquery.py --input data/processed_data.csv
```

This loads the processed CSV into the configured BigQuery table using the BigQuery Python client. The table is created if it does not exist; the script appends rows to an existing table. For repeatable production runs, add an idempotent strategy such as a staging table and `MERGE`.

## 7. Run SQL analytics

Run `sql/analytics_queries.sql` in the BigQuery SQL editor after the table has data. Update the table path if you changed the dataset or table names.

## 8. Example end-to-end workflow

```powershell
python src/ingest.py --file data/sample_data.csv
python src/transform.py --input data/sample_data.csv --output data/processed_data.csv
# Optional cloud upload/event publishing:
python src/ingest.py --file data/sample_data.csv --upload-to-gcs --publish-event
# Optional BigQuery load:
python src/load_bigquery.py --input data/processed_data.csv
python -m unittest discover -s tests -v
```

## Limitations and next improvements

- This is a learning/portfolio project, not a production orchestration system.
- It does not automatically react to every GCS upload unless you configure a notification or trigger.
- It currently handles CSV files and uses a simple append load into BigQuery.
- Add Cloud Scheduler or Workflows orchestration, data-quality metrics, structured logging, retries, dead-letter handling, and idempotent loads as future enhancements.
