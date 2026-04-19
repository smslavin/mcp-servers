from app import mcp
from client import BASE_URL, get_client, handle_response


@mcp.tool()
def get_gear(gear_id: str) -> str:
    """
    Get details for a piece of gear (bike or shoes) including components and distance.

    Args:
        gear_id: The gear ID string (e.g. 'b1234567' for bikes, 'g1234567' for shoes).
            Find gear IDs in the athlete profile from get_athlete.
    """
    with get_client() as c:
        r = c.get(f"{BASE_URL}/gear/{gear_id}")
    return handle_response(r)


@mcp.tool()
def list_athlete_gear() -> str:
    """
    List all bikes and shoes registered to the authenticated athlete,
    including total distance logged on each.
    """
    with get_client() as c:
        r = c.get(f"{BASE_URL}/athlete")
    import json
    athlete = json.loads(handle_response(r))
    gear = {
        "bikes": athlete.get("bikes", []),
        "shoes": athlete.get("shoes", []),
    }
    return json.dumps(gear)
