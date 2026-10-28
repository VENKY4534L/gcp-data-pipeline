"""Upload CSV files to GCS and optionally publish a Pub/Sub event."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from google.cloud import pubsub_v1, storage


def upload_to_gcs(file_path: Path, bucket_name: str, project_id: str) -> str:
    client = storage.Client(project=project_id)
    bucket = client.bucket(bucket_name)
    object_name = file_path.name
    bucket.blob(object_name).upload_from_filename(str(file_path))
    return object_name


def publish_event(project_id: str, topic_name: str, bucket_name: str, object_name: str) -> str:
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(project_id, topic_name)
    payload = json.dumps({"bucket": bucket_name, "object": object_name}).encode("utf-8")
    future = publisher.publish(topic_path, payload, event_type="csv_uploaded")
    return future.result(timeout=30)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--file", required=True, help="CSV file to ingest")
    parser.add_argument("--upload-to-gcs", action="store_true", help="Upload CSV to configured GCS bucket")
    parser.add_argument("--publish-event", action="store_true", help="Publish a Pub/Sub event after upload")
    args = parser.parse_args()

    file_path = Path(args.file)
    if not file_path.is_file():
        parser.error(f"File not found: {file_path}")

    project_id = os.getenv("GCP_PROJECT_ID")
    bucket_name = os.getenv("GCS_BUCKET")
    topic_name = os.getenv("PUBSUB_TOPIC")

    if args.upload_to_gcs:
        if not project_id or not bucket_name:
            parser.error("Set GCP_PROJECT_ID and GCS_BUCKET before using --upload-to-gcs")
        object_name = upload_to_gcs(file_path, bucket_name, project_id)
        print(f"Uploaded gs://{bucket_name}/{object_name}")

        if args.publish_event:
            if not topic_name:
                parser.error("Set PUBSUB_TOPIC before using --publish-event")
            message_id = publish_event(project_id, topic_name, bucket_name, object_name)
            print(f"Published Pub/Sub message ID: {message_id}")
    elif args.publish_event:
        parser.error("--publish-event requires --upload-to-gcs in this starter workflow")
    else:
        print(f"Local ingestion source ready: {file_path}")


if __name__ == "__main__":
    main()
