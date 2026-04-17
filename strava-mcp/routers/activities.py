import json
from datetime import datetime, timezone
from typing import Optional

from app import mcp
from client import BASE_URL, get_client, handle_response


def _to_timestamp(date_str: str) -> int:
    """Convert YYYY-MM-DD string to a Unix timestamp (start of day UTC)."""
    dt = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    return int(dt.timestamp())


# ---------------------------------------------------------------------------
# List / search
# ---------------------------------------------------------------------------

@mcp.tool()
def list_activities(
    after: str,
    before: Optional[str] = None,
    per_page: int = 30,
    page: int = 1,
) -> str:
    """
    List activities for the authenticated athlete in descending date order.

    Args:
        after: Start date YYYY-MM-DD (inclusive).
        before: End date YYYY-MM-DD (inclusive). Defaults to today.
        per_page: Number of activities per page (max 200).
        page: Page number for pagination.
    """
    params: dict = {
        "after": _to_timestamp(after),
        "per_page": min(per_page, 200),
        "page": page,
    }
    if before:
        params["before"] = _to_timestamp(before) + 86400  # include the full day
    with get_client() as c:
        r = c.get(f"{BASE_URL}/athlete/activities", params=params)
    return handle_response(r)


# ---------------------------------------------------------------------------
# Single activity
# ---------------------------------------------------------------------------

@mcp.tool()
def get_activity(activity_id: int, include_all_efforts: bool = False) -> str:
    """
    Get full details for a single activity.

    Args:
        activity_id: The Strava activity ID (integer).
        include_all_efforts: Include all segment efforts, not just PR efforts.
    """
    params: dict = {}
    if include_all_efforts:
        params["include_all_efforts"] = "true"
    with get_client() as c:
        r = c.get(f"{BASE_URL}/activities/{activity_id}", params=params)
    return handle_response(r)


@mcp.tool()
def get_activity_laps(activity_id: int) -> str:
    """
    Get laps for an activity. Laps correspond to intervals in intervals.icu.

    Args:
        activity_id: The Strava activity ID (integer).
    """
    with get_client() as c:
        r = c.get(f"{BASE_URL}/activities/{activity_id}/laps")
    return handle_response(r)


@mcp.tool()
def get_activity_streams(
    activity_id: int,
    keys: Optional[str] = None,
) -> str:
    """
    Get time-series data streams for an activity.

    Args:
        activity_id: The Strava activity ID (integer).
        keys: Comma-separated stream keys to fetch. Available streams:
            time, distance, latlng, altitude, velocity_smooth, heartrate,
            cadence, watts, temp, moving, grade_smooth.
            Defaults to all available streams.
    """
    if not keys:
        keys = "time,distance,altitude,velocity_smooth,heartrate,cadence,watts,temp,moving,grade_smooth"
    params = {"keys": keys, "key_by_type": "true"}
    with get_client() as c:
        r = c.get(f"{BASE_URL}/activities/{activity_id}/streams", params=params)
    return handle_response(r)


@mcp.tool()
def get_activity_zones(activity_id: int) -> str:
    """
    Get heart rate and power zones for an activity.

    Args:
        activity_id: The Strava activity ID (integer).
    """
    with get_client() as c:
        r = c.get(f"{BASE_URL}/activities/{activity_id}/zones")
    return handle_response(r)


@mcp.tool()
def get_activity_comments(activity_id: int, page: int = 1, per_page: int = 30) -> str:
    """
    Get comments on an activity.

    Args:
        activity_id: The Strava activity ID (integer).
        page: Page number.
        per_page: Comments per page (max 200).
    """
    with get_client() as c:
        r = c.get(
            f"{BASE_URL}/activities/{activity_id}/comments",
            params={"page": page, "per_page": min(per_page, 200)},
        )
    return handle_response(r)


@mcp.tool()
def get_activity_kudos(activity_id: int, page: int = 1, per_page: int = 30) -> str:
    """
    Get kudos (likes) on an activity.

    Args:
        activity_id: The Strava activity ID (integer).
        page: Page number.
        per_page: Kudos per page (max 200).
    """
    with get_client() as c:
        r = c.get(
            f"{BASE_URL}/activities/{activity_id}/kudos",
            params={"page": page, "per_page": min(per_page, 200)},
        )
    return handle_response(r)


@mcp.tool()
def update_activity(activity_id: int, payload: str) -> str:
    """
    Update fields on an activity.

    Args:
        activity_id: The Strava activity ID (integer).
        payload: JSON string of fields to update. Editable fields:
            name, type, sport_type, description, gear_id,
            commute (bool), trainer (bool), hide_from_home (bool).
    """
    try:
        data = json.loads(payload)
    except json.JSONDecodeError as e:
        return f"Invalid JSON payload: {e}"
    with get_client() as c:
        r = c.put(f"{BASE_URL}/activities/{activity_id}", json=data)
    return handle_response(r)
