from app import mcp
from client import BASE_URL, get_client, handle_response


@mcp.tool()
def get_athlete() -> str:
    """Get the authenticated athlete's profile."""
    with get_client() as c:
        r = c.get(f"{BASE_URL}/athlete")
    return handle_response(r)


@mcp.tool()
def get_athlete_stats() -> str:
    """
    Get lifetime stats for the authenticated athlete (totals for rides, runs, swims).
    Requires the athlete ID from get_athlete.
    """
    # Fetch athlete id first
    with get_client() as c:
        r = c.get(f"{BASE_URL}/athlete")
    handle_response(r)
    athlete_id = r.json()["id"]

    with get_client() as c:
        r = c.get(f"{BASE_URL}/athletes/{athlete_id}/stats")
    return handle_response(r)


@mcp.tool()
def get_athlete_zones() -> str:
    """Get the authenticated athlete's heart rate and power zones."""
    with get_client() as c:
        r = c.get(f"{BASE_URL}/athlete/zones")
    return handle_response(r)
