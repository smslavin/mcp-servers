import json
import os
from typing import Optional

import httpx
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

load_dotenv()

ATHLETE_ID = os.getenv("INTERVALS_ATHLETE_ID")
API_KEY = os.getenv("INTERVALS_API_KEY")
BASE_URL = "https://intervals.icu/api/v1"

mcp = FastMCP("intervals-mcp")


def _client() -> httpx.Client:
    return httpx.Client(
        auth=("API_KEY", API_KEY),
        headers={"Accept": "application/json"},
        timeout=30,
    )


def _aid(athlete_id: Optional[str]) -> str:
    return athlete_id or ATHLETE_ID


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
    with _client() as c:
        r = c.get(f"{BASE_URL}/athlete/{_aid(athlete_id)}")
    r.raise_for_status()
    return r.text


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
        oldest: Start date YYYY-MM-DD (inclusive).
        newest: End date YYYY-MM-DD (inclusive).
        athlete_id: Athlete ID. Defaults to INTERVALS_ATHLETE_ID env var.
    """
    with _client() as c:
        r = c.get(
            f"{BASE_URL}/athlete/{_aid(athlete_id)}/wellness",
            params={"oldest": oldest, "newest": newest},
        )
    r.raise_for_status()
    return r.text


@mcp.tool()
def get_wellness(date: str, athlete_id: Optional[str] = None) -> str:
    """
    Retrieve a single wellness entry for a specific date.

    Args:
        date: Date YYYY-MM-DD.
        athlete_id: Athlete ID. Defaults to INTERVALS_ATHLETE_ID env var.
    """
    with _client() as c:
        r = c.get(f"{BASE_URL}/athlete/{_aid(athlete_id)}/wellness/{date}")
    r.raise_for_status()
    return r.text


@mcp.tool()
def update_wellness(date: str, payload: str, athlete_id: Optional[str] = None) -> str:
    """
    Create or update a wellness entry for a specific date.

    Args:
        date: Date YYYY-MM-DD.
        payload: JSON string of wellness fields. Common fields:
            weight (kg), restingHR, hrv, hrvSDNN, mentalLoad, physicalLoad,
            sleepSecs, sleepScore, sleepQuality, mood, motivation, soreness,
            fatigue, stress, hydration, kcalConsumed, notes.
        athlete_id: Athlete ID. Defaults to INTERVALS_ATHLETE_ID env var.
    """
    try:
        data = json.loads(payload)
    except json.JSONDecodeError as e:
        return f"Invalid JSON payload: {e}"
    with _client() as c:
        r = c.put(f"{BASE_URL}/athlete/{_aid(athlete_id)}/wellness/{date}", json=data)
    r.raise_for_status()
    return r.text


@mcp.tool()
def bulk_update_wellness(payload: str, athlete_id: Optional[str] = None) -> str:
    """
    Update multiple wellness records in one call. All records must be for the same athlete.

    Args:
        payload: JSON array string of wellness objects. Each object must include an 'id'
            field set to the date (YYYY-MM-DD) plus any wellness fields to set.
        athlete_id: Athlete ID. Defaults to INTERVALS_ATHLETE_ID env var.
    """
    try:
        data = json.loads(payload)
    except json.JSONDecodeError as e:
        return f"Invalid JSON payload: {e}"
    with _client() as c:
        r = c.put(f"{BASE_URL}/athlete/{_aid(athlete_id)}/wellness-bulk", json=data)
    r.raise_for_status()
    return r.text


# ---------------------------------------------------------------------------
# Activities — list / search
# ---------------------------------------------------------------------------

@mcp.tool()
def list_activities(
    oldest: str,
    newest: Optional[str] = None,
    limit: Optional[int] = None,
    fields: Optional[str] = None,
    athlete_id: Optional[str] = None,
) -> str:
    """
    List activities for a date range in descending date order.

    Args:
        oldest: Start date YYYY-MM-DD (inclusive, required).
        newest: End date YYYY-MM-DD (inclusive). Defaults to today.
        limit: Maximum number of activities to return.
        fields: Comma-separated list of fields to include (reduces response size).
        athlete_id: Athlete ID. Defaults to INTERVALS_ATHLETE_ID env var.
    """
    params: dict = {"oldest": oldest}
    if newest:
        params["newest"] = newest
    if limit:
        params["limit"] = limit
    if fields:
        params["fields"] = fields
    with _client() as c:
        r = c.get(f"{BASE_URL}/athlete/{_aid(athlete_id)}/activities", params=params)
    r.raise_for_status()
    return r.text


@mcp.tool()
def search_activities(
    q: str,
    limit: Optional[int] = None,
    athlete_id: Optional[str] = None,
) -> str:
    """
    Search for activities by name or tag. Returns summary info.

    Args:
        q: Search query (name or tag).
        limit: Maximum number of results.
        athlete_id: Athlete ID. Defaults to INTERVALS_ATHLETE_ID env var.
    """
    params: dict = {"q": q}
    if limit:
        params["limit"] = limit
    with _client() as c:
        r = c.get(
            f"{BASE_URL}/athlete/{_aid(athlete_id)}/activities/search", params=params
        )
    r.raise_for_status()
    return r.text


@mcp.tool()
def search_activities_full(
    q: str,
    limit: Optional[int] = None,
    athlete_id: Optional[str] = None,
) -> str:
    """
    Search for activities by name or tag. Returns full activity objects.

    Args:
        q: Search query (name or tag).
        limit: Maximum number of results.
        athlete_id: Athlete ID. Defaults to INTERVALS_ATHLETE_ID env var.
    """
    params: dict = {"q": q}
    if limit:
        params["limit"] = limit
    with _client() as c:
        r = c.get(
            f"{BASE_URL}/athlete/{_aid(athlete_id)}/activities/search-full",
            params=params,
        )
    r.raise_for_status()
    return r.text


@mcp.tool()
def interval_search_activities(
    min_secs: int,
    max_secs: int,
    min_intensity: float,
    max_intensity: float,
    activity_type: Optional[str] = None,
    min_reps: Optional[int] = None,
    max_reps: Optional[int] = None,
    limit: Optional[int] = None,
    athlete_id: Optional[str] = None,
) -> str:
    """
    Find activities that contain intervals matching duration and intensity criteria.

    Args:
        min_secs: Minimum interval duration in seconds.
        max_secs: Maximum interval duration in seconds.
        min_intensity: Minimum interval intensity (0-100 scale, e.g. 80).
        max_intensity: Maximum interval intensity (0-100 scale, e.g. 100).
        activity_type: Filter by sport type (e.g. 'Ride', 'Run').
        min_reps: Minimum number of matching intervals.
        max_reps: Maximum number of matching intervals.
        limit: Maximum number of activities to return.
        athlete_id: Athlete ID. Defaults to INTERVALS_ATHLETE_ID env var.
    """
    params: dict = {
        "minSecs": min_secs,
        "maxSecs": max_secs,
        "minIntensity": min_intensity,
        "maxIntensity": max_intensity,
    }
    if activity_type:
        params["type"] = activity_type
    if min_reps:
        params["minReps"] = min_reps
    if max_reps:
        params["maxReps"] = max_reps
    if limit:
        params["limit"] = limit
    with _client() as c:
        r = c.get(
            f"{BASE_URL}/athlete/{_aid(athlete_id)}/activities/interval-search",
            params=params,
        )
    r.raise_for_status()
    return r.text


@mcp.tool()
def get_activities_by_ids(
    ids: str,
    include_intervals: bool = False,
    athlete_id: Optional[str] = None,
) -> str:
    """
    Fetch multiple activities by ID in one call. Missing activities are ignored.

    Args:
        ids: Comma-separated activity IDs (e.g. 'A123,A456').
        include_intervals: Whether to include interval data in the response.
        athlete_id: Athlete ID. Defaults to INTERVALS_ATHLETE_ID env var.
    """
    params: dict = {}
    if include_intervals:
        params["intervals"] = "true"
    with _client() as c:
        r = c.get(
            f"{BASE_URL}/athlete/{_aid(athlete_id)}/activities/{ids}", params=params
        )
    r.raise_for_status()
    return r.text


# ---------------------------------------------------------------------------
# Activities — single activity CRUD
# ---------------------------------------------------------------------------

@mcp.tool()
def get_activity(
    activity_id: str,
    include_intervals: bool = False,
) -> str:
    """
    Get full details for a single activity.

    Args:
        activity_id: The activity ID (e.g. 'A12345678').
        include_intervals: Whether to include interval data in the response.
    """
    params: dict = {}
    if include_intervals:
        params["intervals"] = "true"
    with _client() as c:
        r = c.get(f"{BASE_URL}/activity/{activity_id}", params=params)
    r.raise_for_status()
    return r.text


@mcp.tool()
def update_activity(activity_id: str, payload: str) -> str:
    """
    Update fields on an existing activity.

    Args:
        activity_id: The activity ID (e.g. 'A12345678').
        payload: JSON string of fields to update. Common fields:
            name, description, type, indoor, perceived_exertion, feel, race, commute.
    """
    try:
        data = json.loads(payload)
    except json.JSONDecodeError as e:
        return f"Invalid JSON payload: {e}"
    with _client() as c:
        r = c.put(f"{BASE_URL}/activity/{activity_id}", json=data)
    r.raise_for_status()
    return r.text


@mcp.tool()
def delete_activity(activity_id: str) -> str:
    """
    Delete an activity permanently.

    Args:
        activity_id: The activity ID (e.g. 'A12345678').
    """
    with _client() as c:
        r = c.delete(f"{BASE_URL}/activity/{activity_id}")
    r.raise_for_status()
    return r.text or "Activity deleted."


# ---------------------------------------------------------------------------
# Activities — streams / intervals
# ---------------------------------------------------------------------------

@mcp.tool()
def get_activity_streams(
    activity_id: str,
    types: Optional[str] = None,
) -> str:
    """
    Get time-series data streams for an activity (power, HR, cadence, speed, etc.).

    Args:
        activity_id: The activity ID (e.g. 'A12345678').
        types: Comma-separated stream types to fetch. Common values:
            time, watts, heartrate, cadence, distance, altitude, latlng,
            velocity_smooth, temp. Omit to fetch all available streams.
    """
    params: dict = {}
    if types:
        params["types"] = types
    with _client() as c:
        r = c.get(f"{BASE_URL}/activity/{activity_id}/streams", params=params)
    r.raise_for_status()
    return r.text


@mcp.tool()
def get_activity_intervals(activity_id: str) -> str:
    """
    Get the computed intervals/laps for an activity.

    Args:
        activity_id: The activity ID (e.g. 'A12345678').
    """
    with _client() as c:
        r = c.get(f"{BASE_URL}/activity/{activity_id}/intervals")
    r.raise_for_status()
    return r.text


@mcp.tool()
def get_activity_interval_stats(
    activity_id: str,
    start_index: int,
    end_index: int,
) -> str:
    """
    Return interval-like stats for a portion of an activity (by stream index).

    Args:
        activity_id: The activity ID.
        start_index: Start stream index.
        end_index: End stream index.
    """
    with _client() as c:
        r = c.get(
            f"{BASE_URL}/activity/{activity_id}/interval-stats",
            params={"start_index": start_index, "end_index": end_index},
        )
    r.raise_for_status()
    return r.text


# ---------------------------------------------------------------------------
# Activities — analysis / curves / histograms
# ---------------------------------------------------------------------------

@mcp.tool()
def get_activity_best_efforts(
    activity_id: str,
    stream: str,
    duration: Optional[int] = None,
    distance: Optional[float] = None,
    count: Optional[int] = None,
    min_value: Optional[float] = None,
) -> str:
    """
    Find best efforts within an activity for a given stream.

    Args:
        activity_id: The activity ID.
        stream: Stream to analyse, e.g. 'watts', 'heartrate', 'velocity_smooth'.
        duration: Duration in seconds to find best effort for.
        distance: Distance in metres to find best effort for.
        count: Number of best efforts to return.
        min_value: Minimum value threshold to count as an effort.
    """
    params: dict = {"stream": stream}
    if duration:
        params["duration"] = duration
    if distance:
        params["distance"] = distance
    if count:
        params["count"] = count
    if min_value:
        params["minValue"] = min_value
    with _client() as c:
        r = c.get(f"{BASE_URL}/activity/{activity_id}/best-efforts", params=params)
    r.raise_for_status()
    return r.text


@mcp.tool()
def get_activity_power_curve(activity_id: str, fatigue: Optional[bool] = None) -> str:
    """
    Get the mean-maximal power curve for an activity.

    Args:
        activity_id: The activity ID.
        fatigue: If true, include fatigue-adjusted curve.
    """
    params: dict = {}
    if fatigue is not None:
        params["fatigue"] = str(fatigue).lower()
    with _client() as c:
        r = c.get(f"{BASE_URL}/activity/{activity_id}/power-curve", params=params)
    r.raise_for_status()
    return r.text


@mcp.tool()
def get_activity_hr_curve(activity_id: str) -> str:
    """
    Get the mean-maximal heart rate curve for an activity.

    Args:
        activity_id: The activity ID.
    """
    with _client() as c:
        r = c.get(f"{BASE_URL}/activity/{activity_id}/hr-curve")
    r.raise_for_status()
    return r.text


@mcp.tool()
def get_activity_pace_curve(activity_id: str, gap: Optional[bool] = None) -> str:
    """
    Get the mean-maximal pace curve for an activity.

    Args:
        activity_id: The activity ID.
        gap: If true, use gradient adjusted pace.
    """
    params: dict = {}
    if gap is not None:
        params["gap"] = str(gap).lower()
    with _client() as c:
        r = c.get(f"{BASE_URL}/activity/{activity_id}/pace-curve", params=params)
    r.raise_for_status()
    return r.text


@mcp.tool()
def get_activity_power_histogram(
    activity_id: str, bucket_size: Optional[int] = None
) -> str:
    """
    Get the power histogram for an activity.

    Args:
        activity_id: The activity ID.
        bucket_size: Histogram bucket width in watts.
    """
    params: dict = {}
    if bucket_size:
        params["bucketSize"] = bucket_size
    with _client() as c:
        r = c.get(f"{BASE_URL}/activity/{activity_id}/power-histogram", params=params)
    r.raise_for_status()
    return r.text


@mcp.tool()
def get_activity_hr_histogram(
    activity_id: str, bucket_size: Optional[int] = None
) -> str:
    """
    Get the heart rate histogram for an activity.

    Args:
        activity_id: The activity ID.
        bucket_size: Histogram bucket width in bpm.
    """
    params: dict = {}
    if bucket_size:
        params["bucketSize"] = bucket_size
    with _client() as c:
        r = c.get(f"{BASE_URL}/activity/{activity_id}/hr-histogram", params=params)
    r.raise_for_status()
    return r.text


@mcp.tool()
def get_activity_pace_histogram(activity_id: str) -> str:
    """
    Get the pace histogram for an activity.

    Args:
        activity_id: The activity ID.
    """
    with _client() as c:
        r = c.get(f"{BASE_URL}/activity/{activity_id}/pace-histogram")
    r.raise_for_status()
    return r.text


@mcp.tool()
def get_activity_power_vs_hr(activity_id: str) -> str:
    """
    Get power vs heart rate data for an activity (useful for aerobic decoupling analysis).

    Args:
        activity_id: The activity ID.
    """
    with _client() as c:
        r = c.get(f"{BASE_URL}/activity/{activity_id}/power-vs-hr")
    r.raise_for_status()
    return r.text


@mcp.tool()
def get_activity_time_at_hr(activity_id: str) -> str:
    """
    Get time-at-heart-rate zone data for an activity.

    Args:
        activity_id: The activity ID.
    """
    with _client() as c:
        r = c.get(f"{BASE_URL}/activity/{activity_id}/time-at-hr")
    r.raise_for_status()
    return r.text


# ---------------------------------------------------------------------------
# Activities — map / weather / segments
# ---------------------------------------------------------------------------

@mcp.tool()
def get_activity_map(
    activity_id: str,
    bounds_only: bool = False,
    include_weather: bool = False,
) -> str:
    """
    Get map data (route coordinates and metadata) for an activity.

    Args:
        activity_id: The activity ID.
        bounds_only: Return only the bounding box, not the full route.
        include_weather: Include weather data in the response.
    """
    params: dict = {}
    if bounds_only:
        params["boundsOnly"] = "true"
    if include_weather:
        params["weather"] = "true"
    with _client() as c:
        r = c.get(f"{BASE_URL}/activity/{activity_id}/map", params=params)
    r.raise_for_status()
    return r.text


@mcp.tool()
def get_activity_weather(activity_id: str) -> str:
    """
    Get weather summary for an activity.

    Args:
        activity_id: The activity ID.
    """
    with _client() as c:
        r = c.get(f"{BASE_URL}/activity/{activity_id}/weather-summary")
    r.raise_for_status()
    return r.text


@mcp.tool()
def get_activity_segments(activity_id: str) -> str:
    """
    Get Strava/local segments matched in an activity.

    Args:
        activity_id: The activity ID.
    """
    with _client() as c:
        r = c.get(f"{BASE_URL}/activity/{activity_id}/segments")
    r.raise_for_status()
    return r.text


# ---------------------------------------------------------------------------
# Activities — messages (comments)
# ---------------------------------------------------------------------------

@mcp.tool()
def get_activity_messages(
    activity_id: str,
    limit: Optional[int] = None,
    since_id: Optional[int] = None,
) -> str:
    """
    List all comments/messages on an activity.

    Args:
        activity_id: The activity ID.
        limit: Maximum number of messages to return.
        since_id: Return only messages with ID greater than this value.
    """
    params: dict = {}
    if limit:
        params["limit"] = limit
    if since_id:
        params["sinceId"] = since_id
    with _client() as c:
        r = c.get(f"{BASE_URL}/activity/{activity_id}/messages", params=params)
    r.raise_for_status()
    return r.text


@mcp.tool()
def post_activity_message(activity_id: str, payload: str) -> str:
    """
    Add a comment/message to an activity.

    Args:
        activity_id: The activity ID.
        payload: JSON string with message fields, e.g. {"message": "Great ride!"}.
    """
    try:
        data = json.loads(payload)
    except json.JSONDecodeError as e:
        return f"Invalid JSON payload: {e}"
    with _client() as c:
        r = c.post(f"{BASE_URL}/activity/{activity_id}/messages", json=data)
    r.raise_for_status()
    return r.text


if __name__ == "__main__":
    mcp.run()
