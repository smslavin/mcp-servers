# strava-mcp

A natural language interface for Strava activity data, built on the Model Context Protocol (MCP). Exposes athlete activities, time-series streams, segment efforts, gear and routes as AI-callable tools, enabling conversational analysis of training history and performance data.

---

## The Problem

Strava is the de facto activity tracking platform for endurance athletes, but accessing its data programmatically requires navigating a REST API, managing OAuth 2.0 token lifecycles and writing code to extract and correlate the metrics that matter. For athletes using [intervals.icu](https://intervals.icu) for training analytics, the situation is compounded: intervals.icu's public API does not proxy Strava-sourced activity data due to Strava's API terms, creating a gap in coverage for raw streams, segment efforts and gear data.

---

## The Solution

strava-mcp connects directly to the Strava API via OAuth 2.0 and exposes it as MCP tools. Used alongside [intervals-mcp](../intervals-mcp/), it completes the picture. intervals.icu for training load, fitness modeling and wellness analytics. Strava for raw activity data, segment performance and gear tracking.

**Example interactions:**

```
"What were my last 10 rides and how did average power trend?"
"Show me my segment efforts on [segment name] over the past year."
"Which bike have I logged the most miles on?"
"What was my heart rate and power profile on last Tuesday's ride?"
"List my starred segments."
"How do my zone distributions compare between this month and last month?"
```

---

## Key Capabilities

| Capability | Description |
|---|---|
| **Activity data** | Full activity details, laps, time-series streams, zone distributions |
| **Segment tracking** | Effort history, PR and KOM rankings, starred segments |
| **Gear management** | Bikes and shoes with total logged distance |
| **Route data** | Route details, elevation profiles, GPS streams |
| **Athlete profile** | Profile, lifetime stats, heart rate and power training zones |

---

## Architecture

```
AI Assistant (Claude Desktop, Claude Code, etc.)
        │
        ▼
strava-mcp (FastMCP / stdio)
        │
        ▼
Strava REST API (api.strava.com)
        │
        ├── OAuth 2.0 token management (auto-refresh)
        └── Activity streams, segments, gear, routes
```

### Design Decisions

**OAuth 2.0 with automatic token refresh.** Strava access tokens expire every 6 hours. The server checks token expiry before each request and exchanges the refresh token for a new access token transparently, persisting the updated token back to `.env`. No manual re-authorization is required after the initial setup.

**Separate server from intervals-mcp.** The intervals.icu public API does not expose Strava-sourced activity data. Rather than treat this as a limitation, strava-mcp accesses Strava directly and is designed to run alongside intervals-mcp. The two servers complement each other: intervals.icu for analytics and training load modeling, Strava for raw data and segment history.

**Domain-separated routers.** Tools are organized by concern (`athlete`, `activities`, `segments`, `gear`, `routes`). Each module is independently maintainable and the separation maps cleanly to Strava's own API resource groupings.

**Errors surface as exceptions.** Tool functions raise `RuntimeError` on API failures rather than returning error strings. This ensures the exact Strava API error reaches the AI assistant rather than being paraphrased or fabricated.

---

## Technology Stack

| Component | Technology |
|---|---|
| MCP Server | Python, [FastMCP](https://github.com/jlowin/fastmcp) |
| HTTP Client | [httpx](https://www.python-httpx.org) |
| Activity Platform | [Strava API v3](https://developers.strava.com) |
| Auth | OAuth 2.0 with refresh token rotation |
| Credential Management | python-dotenv with automatic `.env` updates on token refresh |
| Runtime | Python 3.11, Conda |

---

## MCP Tools

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
| `get_activity_laps` | Get laps and lap-level metrics |
| `get_activity_streams` | Time-series data (power, HR, cadence, speed, altitude, etc.) |
| `get_activity_zones` | Heart rate and power zone distribution for an activity |
| `get_activity_segment_efforts` | All segment efforts with PR/KOM rankings |
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

---

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

    > **Running in WSL?** Visit the authorization URL printed to the terminal. After authorizing, copy the `code=` value from the browser's redirect URL and run:
    > ```bash
    > python auth.py --code YOUR_CODE_HERE
    > ```

### Connecting from Claude Desktop (Windows, server running in WSL)

```json
{
  "mcpServers": {
    "strava": {
      "command": "wsl.exe",
      "args": [
        "/home/yourname/miniconda3/envs/strava-mcp/bin/python",
        "/home/yourname/code/mcp-servers/strava-mcp/server.py"
      ]
    }
  }
}
```

### Connecting from Claude Code or Claude Desktop (macOS/Linux)

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

---

## Limitations and Known Constraints

- **Strava API rate limits apply.** The Strava API enforces a 200-request / 15-minute and 2,000-request / day limit. Heavy use of stream or segment effort tools in a single session can approach these limits.
- **`activity:read_all` scope required.** The initial OAuth authorization must include `activity:read_all` to access private activities. Public-only activities are available with the default `read` scope but will miss private data.
- **`update_activity` writes to Strava.** This is the only write operation in the server. It modifies activity metadata (name, description, gear assignment, sport type) on the authenticated account. Use with care in automated workflows.
- **No real-time data.** The Strava API exposes recorded activity data only. Live GPS or sensor streams are not available through this interface.
- **Webhook events not supported.** The server is request-driven. It does not subscribe to Strava webhook events or proactively notify on new activity uploads.

---

## Roadmap Considerations

- **Cross-source analysis** — agent-level orchestration joining Strava activity streams with intervals.icu training load and HRV4Training recovery data in a single conversation
- **Segment performance modeling** — correlate CTL/ATL/TSB (fitness model from intervals.icu) with segment PR history to evaluate whether the fitness model predicts performance
- **Gear maintenance tracking** — alert when component distance thresholds are approaching based on logged mileage
- **Multi-athlete support** — token management for coaching use cases where a single assistant needs access to multiple athlete accounts

---

## License

MIT
