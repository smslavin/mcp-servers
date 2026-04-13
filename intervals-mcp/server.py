import os
from typing import Optional
import httpx
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

load_dotenv()

ATHLETE_ID = os.getenv("INTERVALS_ATHLETE_ID")
API_KEY = os.getenv("INTERVALS_API_KEY")
BASE_URL = "https://intervals.icu/api/v1"

mcp = FastMCP("intervals-mcp")


def _client() -> httpx.Client:
    """Return an authenticated httpx client."""
    return httpx.Client(
        auth=("API_KEY", API_KEY),
        headers={"Accept": "application/json"},
        timeout=30,
    )


def _athlete_id(athlete_id: Optional[str]) -> str:
    return athlete_id or ATHLETE_ID


# ---------------------------------------------------------------------------
# Wellness
# ---------------------------------------------------------------------------

@mcp.tool()
def list_wellness(
    oldest: str,
    newest: str,
    athlete_id: Optional[str] = None,
) -> str:
    """
    Retrieve wellness entries for a date range.

    Args:
        oldest: Start date in YYYY-MM-DD format (inclusive).
        newest: End date in YYYY-MM-DD format (inclusive).
        athlete_id: Athlete ID (e.g. 'i12345'). Defaults to INTERVALS_ATHLETE_ID env var.
    """
    aid = _athlete_id(athlete_id)
    with _client() as client:
        resp = client.get(
            f"{BASE_URL}/athlete/{aid}/wellness",
            params={"oldest": oldest, "newest": newest},
        )
    resp.raise_for_status()
    return resp.text


@mcp.tool()
def get_wellness(
    date: str,
    athlete_id: Optional[str] = None,
) -> str:
    """
    Retrieve a single wellness entry for a specific date.

    Args:
        date: Date in YYYY-MM-DD format.
        athlete_id: Athlete ID (e.g. 'i12345'). Defaults to INTERVALS_ATHLETE_ID env var.
    """
    aid = _athlete_id(athlete_id)
    with _client() as client:
        resp = client.get(f"{BASE_URL}/athlete/{aid}/wellness/{date}")
    resp.raise_for_status()
    return resp.text


@mcp.tool()
def update_wellness(
    date: str,
    payload: str,
    athlete_id: Optional[str] = None,
) -> str:
    """
    Create or update a wellness entry for a specific date.

    Args:
        date: Date in YYYY-MM-DD format.
        payload: JSON string of wellness fields to set. Common fields include:
            weight (kg), restingHR, hrv, hrvSDNN, mentalLoad, physicalLoad,
            sleepSecs, sleepScore, sleepQuality, mood, motivation, soreness,
            fatigue, stress, hydration, kcalConsumed, notes.
        athlete_id: Athlete ID (e.g. 'i12345'). Defaults to INTERVALS_ATHLETE_ID env var.
    """
    import json
    aid = _athlete_id(athlete_id)
    try:
        data = json.loads(payload)
    except json.JSONDecodeError as e:
        return f"Invalid JSON payload: {e}"
    with _client() as client:
        resp = client.put(
            f"{BASE_URL}/athlete/{aid}/wellness/{date}",
            json=data,
        )
    resp.raise_for_status()
    return resp.text


# ---------------------------------------------------------------------------
# Activities
# ---------------------------------------------------------------------------

@mcp.tool()
def list_activities(
    oldest: str,
    newest: str,
    athlete_id: Optional[str] = None,
) -> str:
    """
    List activities for a date range.

    Args:
        oldest: Start date in YYYY-MM-DD format (inclusive).
        newest: End date in YYYY-MM-DD format (inclusive).
        athlete_id: Athlete ID (e.g. 'i12345'). Defaults to INTERVALS_ATHLETE_ID env var.
    """
    aid = _athlete_id(athlete_id)
    with _client() as client:
        resp = client.get(
            f"{BASE_URL}/athlete/{aid}/activities",
            params={"oldest": oldest, "newest": newest},
        )
    resp.raise_for_status()
    return resp.text


@mcp.tool()
def get_activity(
    activity_id: str,
    athlete_id: Optional[str] = None,
) -> str:
    """
    Get full details for a single activity.

    Args:
        activity_id: The activity ID (e.g. 'A12345678').
        athlete_id: Athlete ID (e.g. 'i12345'). Defaults to INTERVALS_ATHLETE_ID env var.
    """
    aid = _athlete_id(athlete_id)
    with _client() as client:
        resp = client.get(f"{BASE_URL}/athlete/{aid}/activity/{activity_id}")
    resp.raise_for_status()
    return resp.text


@mcp.tool()
def get_activity_streams(
    activity_id: str,
    types: Optional[str] = None,
    athlete_id: Optional[str] = None,
) -> str:
    """
    Get time-series data streams for an activity (power, HR, cadence, speed, etc.).

    Args:
        activity_id: The activity ID (e.g. 'A12345678').
        types: Comma-separated list of stream types to fetch. Common values:
            time, watts, heartrate, cadence, distance, altitude, latlng,
            velocity_smooth, temp. Omit to fetch all available streams.
        athlete_id: Athlete ID (e.g. 'i12345'). Defaults to INTERVALS_ATHLETE_ID env var.
    """
    aid = _athlete_id(athlete_id)
    params = {}
    if types:
        params["types"] = types
    with _client() as client:
        resp = client.get(
            f"{BASE_URL}/athlete/{aid}/activity/{activity_id}/streams",
            params=params,
        )
    resp.raise_for_status()
    return resp.text


@mcp.tool()
def update_activity(
    activity_id: str,
    payload: str,
    athlete_id: Optional[str] = None,
) -> str:
    """
    Update fields on an existing activity.

    Args:
        activity_id: The activity ID (e.g. 'A12345678').
        payload: JSON string of fields to update. Common fields:
            name, description, type, indoor, perceived_exertion, feel,
            race, commute, ignore_hrv.
        athlete_id: Athlete ID (e.g. 'i12345'). Defaults to INTERVALS_ATHLETE_ID env var.
    """
    import json
    aid = _athlete_id(athlete_id)
    try:
        data = json.loads(payload)
    except json.JSONDecodeError as e:
        return f"Invalid JSON payload: {e}"
    with _client() as client:
        resp = client.put(
            f"{BASE_URL}/athlete/{aid}/activity/{activity_id}",
            json=data,
        )
    resp.raise_for_status()
    return resp.text


@mcp.tool()
def get_activity_intervals(
    activity_id: str,
    athlete_id: Optional[str] = None,
) -> str:
    """
    Get the computed intervals/laps for an activity.

    Args:
        activity_id: The activity ID (e.g. 'A12345678').
        athlete_id: Athlete ID (e.g. 'i12345'). Defaults to INTERVALS_ATHLETE_ID env var.
    """
    aid = _athlete_id(athlete_id)
    with _client() as client:
        resp = client.get(
            f"{BASE_URL}/athlete/{aid}/activity/{activity_id}/intervals"
        )
    resp.raise_for_status()
    return resp.text


# ---------------------------------------------------------------------------
# Athlete
# ---------------------------------------------------------------------------

@mcp.tool()
def get_athlete(athlete_id: Optional[str] = None) -> str:
    """
    Get profile and settings for the athlete.

    Args:
        athlete_id: Athlete ID (e.g. 'i12345'). Defaults to INTERVALS_ATHLETE_ID env var.
    """
    aid = _athlete_id(athlete_id)
    with _client() as client:
        resp = client.get(f"{BASE_URL}/athlete/{aid}")
    resp.raise_for_status()
    return resp.text


if __name__ == "__main__":
    mcp.run()
