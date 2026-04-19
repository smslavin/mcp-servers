import csv
import glob
import io
import json
import os
import time
from datetime import date
from typing import Optional

import httpx
from app import mcp
from dotenv import set_key

ENV_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")

def _cfg(key: str) -> str:
    return os.getenv(key, "")

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


def _dropbox_access_token() -> str:
    refresh_token = _cfg("DROPBOX_REFRESH_TOKEN")
    if not refresh_token:
        # Long-lived token generated from the Dropbox developer console
        return _cfg("DROPBOX_ACCESS_TOKEN")

    expires_at = int(_cfg("DROPBOX_TOKEN_EXPIRES_AT") or "0")
    if time.time() < expires_at - 60:
        return _cfg("DROPBOX_ACCESS_TOKEN")

    r = httpx.post(
        "https://api.dropboxapi.com/oauth2/token",
        data={"grant_type": "refresh_token", "refresh_token": refresh_token},
        auth=(_cfg("DROPBOX_APP_KEY"), _cfg("DROPBOX_APP_SECRET")),
    )
    if r.is_error:
        raise RuntimeError(f"Dropbox token refresh failed: {r.status_code} {r.text}")

    data = r.json()
    access_token = data["access_token"]
    expires_at = int(time.time()) + int(data.get("expires_in", 14400))
    set_key(ENV_PATH, "DROPBOX_ACCESS_TOKEN", access_token)
    set_key(ENV_PATH, "DROPBOX_TOKEN_EXPIRES_AT", str(expires_at))
    os.environ["DROPBOX_ACCESS_TOKEN"] = access_token
    os.environ["DROPBOX_TOKEN_EXPIRES_AT"] = str(expires_at)
    return access_token


def _get_csv_content() -> str:
    """Return CSV content as a string, from local dir or Dropbox."""
    if _cfg("HRV4TRAINING_CSV_DIR"):
        candidates = glob.glob(os.path.join(_cfg("HRV4TRAINING_CSV_DIR"), "*.csv"))
        if not candidates:
            raise RuntimeError(f"No CSV files found in {_cfg('HRV4TRAINING_CSV_DIR')}")
        path = max(candidates, key=os.path.getmtime)
        with open(path, encoding="utf-8") as f:
            return f.read()

    if _cfg("DROPBOX_APP_KEY"):
        token = _dropbox_access_token()

        # Find most recently modified CSV in app folder
        r = httpx.post(
            "https://api.dropboxapi.com/2/files/list_folder",
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            json={"path": ""},
        )
        if r.is_error:
            raise RuntimeError(f"Dropbox list_folder failed: {r.status_code} {r.text}")

        entries = [
            e for e in r.json().get("entries", [])
            if e[".tag"] == "file" and e["name"].endswith(".csv")
        ]
        if not entries:
            raise RuntimeError("No CSV files found in Dropbox app folder")

        latest = max(entries, key=lambda e: e["server_modified"])

        r = httpx.post(
            "https://content.dropboxapi.com/2/files/download",
            headers={
                "Authorization": f"Bearer {token}",
                "Dropbox-API-Arg": json.dumps({"path": latest["id"]}),
            },
        )
        if r.is_error:
            raise RuntimeError(f"Dropbox download failed: {r.status_code} {r.text}")

        return r.text

    raise RuntimeError(
        "No HRV source configured. Set HRV4TRAINING_CSV_DIR or DROPBOX_APP_KEY in .env"
    )


@mcp.tool()
def get_hrv_data(
    after: Optional[str] = None,
    before: Optional[str] = None,
    include_rest_days: bool = False,
) -> str:
    """
    Get HRV4Training daily data. Reads from a local CSV directory or Dropbox
    app folder depending on what is configured in .env.
    Returns HRV metrics (rMSSD, SDNN), recovery score, sleep, and subjective
    wellness markers (fatigue, muscle soreness, mental energy).

    Args:
        after: Start date YYYY-MM-DD (inclusive).
        before: End date YYYY-MM-DD (inclusive).
        include_rest_days: Include days with no HRV measurement (rMSSD is null).
            Default False returns only days with an actual reading.
    """
    after_d = date.fromisoformat(after) if after else None
    before_d = date.fromisoformat(before) if before else None

    content = _get_csv_content()
    reader = csv.DictReader(io.StringIO(content))
    reader.fieldnames = [h.strip() for h in reader.fieldnames]

    rows = []
    for row in reader:
        row_date_str = row["date"].split(" ")[0]
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
