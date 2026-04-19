from app import mcp
from client import BASE_URL, get_client, handle_response


@mcp.tool()
def list_routes(per_page: int = 30, page: int = 1) -> str:
    """
    List routes created by the authenticated athlete.

    Args:
        per_page: Number of results per page (max 200).
        page: Page number for pagination.
    """
    with get_client() as c:
        athlete_r = c.get(f"{BASE_URL}/athlete")
    athlete_id = handle_response(athlete_r)
    import json
    athlete_id = json.loads(athlete_id)["id"]

    with get_client() as c:
        r = c.get(
            f"{BASE_URL}/athletes/{athlete_id}/routes",
            params={"per_page": min(per_page, 200), "page": page},
        )
    return handle_response(r)


@mcp.tool()
def get_route(route_id: int) -> str:
    """
    Get details for a route (name, description, distance, elevation, map).

    Args:
        route_id: The Strava route ID (integer).
    """
    with get_client() as c:
        r = c.get(f"{BASE_URL}/routes/{route_id}")
    return handle_response(r)


@mcp.tool()
def get_route_streams(route_id: int) -> str:
    """
    Get time-series streams for a route (latlng, distance, altitude).

    Args:
        route_id: The Strava route ID (integer).
    """
    with get_client() as c:
        r = c.get(f"{BASE_URL}/routes/{route_id}/streams")
    return handle_response(r)
