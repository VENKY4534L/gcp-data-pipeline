"""Validate and clean sample CSV data for the GCP ETL pipeline."""
from __future__ import annotations

import argparse
import logging
from pathlib import Path

import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
REQUIRED_COLUMNS = ["record_id", "customer", "amount", "event_date", "region"]


def transform_dataframe(frame: pd.DataFrame) -> pd.DataFrame:
    """Normalize, validate, and deduplicate records."""
    frame = frame.copy()
    frame.columns = [str(col).strip().lower() for col in frame.columns]

    missing = [col for col in REQUIRED_COLUMNS if col not in frame.columns]
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(missing)}")

    frame["record_id"] = pd.to_numeric(frame["record_id"], errors="coerce")
    frame["amount"] = pd.to_numeric(frame["amount"], errors="coerce")
    frame["event_date"] = pd.to_datetime(frame["event_date"], errors="coerce").dt.date
    for col in ("customer", "region"):
        frame[col] = frame[col].astype("string").str.strip()
        frame[col] = frame[col].replace("", pd.NA)

    valid = (
        frame["record_id"].notna()
        & frame["amount"].notna()
        & frame["event_date"].notna()
        & frame["customer"].notna()
        & frame["region"].notna()
        & (frame["amount"] >= 0)
    )
    dropped = int((~valid).sum())
    if dropped:
        logging.warning("Excluded %d invalid record(s).", dropped)

    cleaned = frame.loc[valid, REQUIRED_COLUMNS].drop_duplicates(subset=["record_id"])
    cleaned = cleaned.sort_values("record_id").reset_index(drop=True)
    return cleaned


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="Path to source CSV")
    parser.add_argument("--output", required=True, help="Path for cleaned CSV")
    args = parser.parse_args()

    source = Path(args.input)
    destination = Path(args.output)
    if not source.exists():
        parser.error(f"Input file does not exist: {source}")

    cleaned = transform_dataframe(pd.read_csv(source))
    destination.parent.mkdir(parents=True, exist_ok=True)
    cleaned.to_csv(destination, index=False)
    logging.info("Wrote %d cleaned record(s) to %s", len(cleaned), destination)


if __name__ == "__main__":
    main()
