# strava-mcp

An [MCP](https://modelcontextprotocol.io/) server for the [Strava](https://www.strava.com) fitness platform. Exposes the Strava API as tools so AI agents can read athlete profiles, activities, lap data, time-series streams, and training zones.

> **Note:** Strava activity data is not accessible through the intervals.icu API. Use this server alongside [intervals-mcp](../intervals-mcp/) to get full coverage — intervals.icu for wellness, planning, and fitness analytics; Strava for raw activity data and streams.

## Tools

### Athlete
| Tool | Description |
|---|---|
| `get_athlete` | Get the authenticated athlete's profile |
| `get_athlete_stats` | Lifetime stats (total rides, runs, swims, distances) |
| `get_athlete_zones` | Heart rate and power training zones |

### Activities
| Tool | Description |
|---|---|
| `list_activities` | List activities for a date range |
| `get_activity` | Get full details for a single activity |
| `get_activity_laps` | Get laps (equivalent to intervals in intervals.icu) |
| `get_activity_streams` | Time-series data (power, HR, cadence, speed, altitude, etc.) |
| `get_activity_zones` | Heart rate and power zone distribution for an activity |
| `get_activity_segment_efforts` | All segment efforts for an activity with PR/KOM rankings |
| `get_activity_comments` | List comments on an activity |
| `get_activity_kudos` | List kudos on an activity |
| `update_activity` | Update activity fields (name, type, description, gear, etc.) |

### Segments
| Tool | Description |
|---|---|
| `get_segment` | Get segment details (name, distance, grade, elevation) |
| `get_segment_effort` | Get a single segment effort by ID |
| `list_segment_efforts` | List the athlete's efforts on a segment with optional date filter |
| `list_starred_segments` | List segments starred by the athlete |

### Gear
| Tool | Description |
|---|---|
| `list_athlete_gear` | List all bikes and shoes with total logged distance |
| `get_gear` | Get details for a specific piece of gear |

### Routes
| Tool | Description |
|---|---|
| `list_routes` | List routes created by the athlete |
| `get_route` | Get route details (name, distance, elevation, map) |
| `get_route_streams` | Get streams for a route (latlng, distance, altitude) |

## Setup

### Prerequisites

- [Conda](https://docs.conda.io/en/latest/miniconda.html)
- A Strava account
- A Strava API application ([strava.com/settings/api](https://www.strava.com/settings/api))
  - Set **Authorization Callback Domain** to `localhost`

### Installation

1. Create the conda environment:
    ```bash
    conda env create -f environment.yml
    conda activate strava-mcp
    ```

2. Configure credentials:
    ```bash
    cp .env.example .env
    ```
    Edit `.env` and fill in your `STRAVA_CLIENT_ID` and `STRAVA_CLIENT_SECRET` from the Strava API settings page.

3. Authorize the app (one-time):
    ```bash
    python auth.py
    ```
    A browser window will open asking you to authorize. After approving, tokens are saved to `.env` automatically.

    > **Running in WSL?** `auth.py` can't open a browser directly. Instead, visit the authorization URL manually — it will be printed to the terminal. After authorizing on Strava, copy the `code=` value from the browser's address bar and run:
    > ```bash
    > python auth.py --code YOUR_CODE_HERE
    > ```
    > Or exchange the code manually — see [Manual token exchange](#manual-token-exchange) below.

## Usage

Run the server over stdio:
```bash
conda activate strava-mcp
python server.py
```

Tokens refresh automatically — when the access token expires (every 6 hours) the server exchanges the refresh token for a new one and updates `.env` transparently.

### Connecting from Claude Code

Add to your MCP config (`.claude/settings.json` or `~/.claude.json`):

```json
{
  "mcpServers": {
    "strava": {
      "command": "/path/to/miniconda3/envs/strava-mcp/bin/python",
      "args": ["/path/to/mcp-servers/strava-mcp/server.py"]
    }
  }
}
```

### Connecting from Claude Desktop (macOS/Linux)

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "strava": {
      "command": "/path/to/miniconda3/envs/strava-mcp/bin/python",
      "args": ["/path/to/mcp-servers/strava-mcp/server.py"]
    }
  }
}
```

### Connecting from Claude Desktop (Windows, server running in WSL)

```json
{
  "mcpServers": {
    "strava": {
      "command": "wsl.exe",
      "args": [
        "/home/seanslavin/miniconda3/envs/strava-mcp/bin/python",
        "/home/seanslavin/code/mcp-servers/strava-mcp/server.py"
      ]
    }
  }
}
```

## Manual token exchange

If running in WSL or a headless environment, authorize manually:

1. Visit this URL in a browser (replace `YOUR_CLIENT_ID`):
    ```
    https://www.strava.com/oauth/authorize?client_id=YOUR_CLIENT_ID&redirect_uri=http://localhost:8765/callback&response_type=code&scope=activity:read_all
    ```
2. After authorizing, copy the `code=` value from the redirect URL.
3. Exchange it for tokens:
    ```bash
    conda activate strava-mcp
    python - <<'EOF'
    import httpx
    from dotenv import set_key, load_dotenv
    import os

    load_dotenv(".env")
    r = httpx.post("https://www.strava.com/oauth/token", data={
        "client_id": os.getenv("STRAVA_CLIENT_ID"),
        "client_secret": os.getenv("STRAVA_CLIENT_SECRET"),
        "code": "PASTE_CODE_HERE",
        "grant_type": "authorization_code",
    })
    d = r.json()
    set_key(".env", "STRAVA_ACCESS_TOKEN", d["access_token"])
    set_key(".env", "STRAVA_REFRESH_TOKEN", d["refresh_token"])
    set_key(".env", "STRAVA_TOKEN_EXPIRES_AT", str(d["expires_at"]))
    print("Done.")
    EOF
    ```
