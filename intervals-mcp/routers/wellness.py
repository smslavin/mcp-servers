import json
from typing import Optional

from app import mcp
from client import athlete_id, get_client, BASE_URL


@mcp.tool()
def list_wellness(
    oldest: str,
    newest: str,
    athlete_id_override: Optional[str] = None,
) -> str:
    """
    Retrieve wellness entries for a date range.

    Args:
        oldest: Start date YYYY-MM-DD (inclusive).
        newest: End date YYYY-MM-DD (inclusive).
        athlete_id_override: Athlete ID. Defaults to INTERVALS_ATHLETE_ID env var.
    """
    with get_client() as c:
        r = c.get(
            f"{BASE_URL}/athlete/{athlete_id(athlete_id_override)}/wellness",
            params={"oldest": oldest, "newest": newest},
        )
    r.raise_for_status()
    return r.text


@mcp.tool()
def get_wellness(date: str, athlete_id_override: Optional[str] = None) -> str:
    """
    Retrieve a single wellness entry for a specific date.

    Args:
        date: Date YYYY-MM-DD.
        athlete_id_override: Athlete ID. Defaults to INTERVALS_ATHLETE_ID env var.
    """
    with get_client() as c:
        r = c.get(f"{BASE_URL}/athlete/{athlete_id(athlete_id_override)}/wellness/{date}")
    r.raise_for_status()
    return r.text


@mcp.tool()
def update_wellness(
    date: str,
    payload: str,
    athlete_id_override: Optional[str] = None,
) -> str:
    """
    Create or update a wellness entry for a specific date.

    Args:
        date: Date YYYY-MM-DD.
        payload: JSON string of wellness fields. Common fields:
            weight (kg), restingHR, hrv, hrvSDNN, mentalLoad, physicalLoad,
            sleepSecs, sleepScore, sleepQuality, mood, motivation, soreness,
            fatigue, stress, hydration, kcalConsumed, notes.
        athlete_id_override: Athlete ID. Defaults to INTERVALS_ATHLETE_ID env var.
    """
    try:
        data = json.loads(payload)
    except json.JSONDecodeError as e:
        return f"Invalid JSON payload: {e}"
    with get_client() as c:
        r = c.put(
            f"{BASE_URL}/athlete/{athlete_id(athlete_id_override)}/wellness/{date}",
            json=data,
        )
    r.raise_for_status()
    return r.text


@mcp.tool()
def bulk_update_wellness(
    payload: str,
    athlete_id_override: Optional[str] = None,
) -> str:
    """
    Update multiple wellness records in one call. All records must be for the same athlete.

    Args:
        payload: JSON array string of wellness objects. Each object must include an 'id'
            field set to the date (YYYY-MM-DD) plus any wellness fields to set.
        athlete_id_override: Athlete ID. Defaults to INTERVALS_ATHLETE_ID env var.
    """
    try:
        data = json.loads(payload)
    except json.JSONDecodeError as e:
        return f"Invalid JSON payload: {e}"
    with get_client() as c:
        r = c.put(
            f"{BASE_URL}/athlete/{athlete_id(athlete_id_override)}/wellness-bulk",
            json=data,
        )
    r.raise_for_status()
    return r.text
