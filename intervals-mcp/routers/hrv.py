import csv
import glob
import json
import os
from datetime import date
from typing import Optional

from app import mcp

HRV_CSV_DIR = os.getenv("HRV4TRAINING_CSV_DIR", "")

KEEP_COLUMNS = [
    "date",
    "HR",
    "rMSSD",
    "SDNN",
    "HRV4T_Recovery_Points",
    "sleep_quality",
    "sleep_time",
    "mental_energy",
    "muscle_soreness",
    "fatigue",
    "physical_condition",
    "training",
    "trainingRPE",
    "trainingTSS",
    "advice",
]


def _parse_value(v: str):
    v = v.strip()
    if v in ("-", ""):
        return None
    try:
        return int(v)
    except ValueError:
        pass
    try:
        return float(v)
    except ValueError:
        pass
    return v


@mcp.tool()
def get_hrv_data(
    after: Optional[str] = None,
    before: Optional[str] = None,
    include_rest_days: bool = False,
) -> str:
    """
    Get HRV4Training daily data from the configured CSV export.
    Returns HRV metrics (rMSSD, SDNN), recovery score, sleep, and subjective
    wellness markers (fatigue, muscle soreness, mental energy).

    Args:
        after: Start date YYYY-MM-DD (inclusive).
        before: End date YYYY-MM-DD (inclusive).
        include_rest_days: Include days with no HRV measurement (rMSSD is null).
            Default False returns only days with an actual reading.
    """
    if not HRV_CSV_DIR:
        raise RuntimeError("HRV4TRAINING_CSV_DIR is not set in .env")
    candidates = glob.glob(os.path.join(HRV_CSV_DIR, "*.csv"))
    if not candidates:
        raise RuntimeError(f"No CSV files found in {HRV_CSV_DIR}")
    HRV_CSV_PATH = max(candidates, key=os.path.getmtime)

    after_d = date.fromisoformat(after) if after else None
    before_d = date.fromisoformat(before) if before else None

    rows = []
    with open(HRV_CSV_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        # Strip whitespace from fieldnames (CSV has spaces after commas)
        reader.fieldnames = [h.strip() for h in reader.fieldnames]
        for row in reader:
            row_date_str = row["date"].split(" ")[0]  # "2025-12-11 00:01:00 +0000" → "2025-12-11"
            try:
                row_date = date.fromisoformat(row_date_str)
            except ValueError:
                continue

            if after_d and row_date < after_d:
                continue
            if before_d and row_date > before_d:
                continue

            record = {col: _parse_value(row.get(col, "-")) for col in KEEP_COLUMNS}
            record["date"] = row_date_str

            if not include_rest_days and record.get("rMSSD") is None:
                continue

            rows.append(record)

    return json.dumps(rows)
