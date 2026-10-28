"""Append a cleaned CSV file to a BigQuery table."""
from __future__ import annotations

import argparse
import os
from pathlib import Path

from google.cloud import bigquery


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="Path to processed CSV")
    args = parser.parse_args()

    project_id = os.getenv("GCP_PROJECT_ID")
    dataset_id = os.getenv("BIGQUERY_DATASET")
    table_id = os.getenv("BIGQUERY_TABLE", "processed_records")
    if not project_id or not dataset_id:
        parser.error("Set GCP_PROJECT_ID and BIGQUERY_DATASET before loading BigQuery")
    source = Path(args.input)
    if not source.is_file():
        parser.error(f"Input file not found: {source}")

    client = bigquery.Client(project=project_id)
    table_ref = f"{project_id}.{dataset_id}.{table_id}"
    schema = [
        bigquery.SchemaField("record_id", "INTEGER", mode="REQUIRED"),
        bigquery.SchemaField("customer", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("amount", "FLOAT", mode="REQUIRED"),
        bigquery.SchemaField("event_date", "DATE", mode="REQUIRED"),
        bigquery.SchemaField("region", "STRING", mode="REQUIRED"),
    ]
    job_config = bigquery.LoadJobConfig(
        schema=schema,
        source_format=bigquery.SourceFormat.CSV,
        skip_leading_rows=1,
        write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
    )
    with source.open("rb") as csv_file:
        job = client.load_table_from_file(csv_file, table_ref, job_config=job_config)
    job.result()
    print(f"Loaded {job.output_rows} row(s) into {table_ref}")


if __name__ == "__main__":
    main()
