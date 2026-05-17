from typing import Optional

from pydantic import BaseModel

from app import mcp
from client import athlete_id, get_client, handle_response, BASE_URL


class WellnessUpdate(BaseModel):
    weight: Optional[float] = None
    restingHR: Optional[int] = None
    hrv: Optional[float] = None
    hrvSDNN: Optional[float] = None
    mentalLoad: Optional[int] = None
    physicalLoad: Optional[int] = None
    sleepSecs: Optional[int] = None
    sleepScore: Optional[float] = None
    sleepQuality: Optional[int] = None
    mood: Optional[int] = None
    motivation: Optional[int] = None
    soreness: Optional[int] = None
    fatigue: Optional[int] = None
    stress: Optional[int] = None
    hydration: Optional[int] = None
    kcalConsumed: Optional[int] = None
    notes: Optional[str] = None


class WellnessUpdateItem(WellnessUpdate):
    id: str  # date YYYY-MM-DD


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
    return handle_response(r)


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
    return handle_response(r)


@mcp.tool()
def update_wellness(
    date: str,
    updates: WellnessUpdate,
    athlete_id_override: Optional[str] = None,
) -> str:
    """
    Create or update a wellness entry for a specific date.

    Args:
        date: Date YYYY-MM-DD.
        updates: Wellness fields to set. All fields are optional — only provided
            fields are written. weight in kg; sleepSecs in seconds; sleepQuality,
            mood, motivation, soreness, fatigue, stress, hydration on a 1-5 scale;
            mentalLoad and physicalLoad on a 0-100 scale.
        athlete_id_override: Athlete ID. Defaults to INTERVALS_ATHLETE_ID env var.
    """
    with get_client() as c:
        r = c.put(
            f"{BASE_URL}/athlete/{athlete_id(athlete_id_override)}/wellness/{date}",
            json=updates.model_dump(exclude_none=True),
        )
    return handle_response(r)


@mcp.tool()
def bulk_update_wellness(
    updates: list[WellnessUpdateItem],
    athlete_id_override: Optional[str] = None,
) -> str:
    """
    Update multiple wellness records in one call.

    Args:
        updates: List of wellness entries to write. Each entry must include an 'id'
            field set to the date (YYYY-MM-DD) plus any wellness fields to set.
            All wellness fields are optional; only provided fields are written.
        athlete_id_override: Athlete ID. Defaults to INTERVALS_ATHLETE_ID env var.
    """
    data = [item.model_dump(exclude_none=True) for item in updates]
    with get_client() as c:
        r = c.put(
            f"{BASE_URL}/athlete/{athlete_id(athlete_id_override)}/wellness-bulk",
            json=data,
        )
    return handle_response(r)
