# intervals-mcp

A natural language interface for endurance training data, built on the Model Context Protocol (MCP). Connects [intervals.icu](https://intervals.icu) training analytics and [HRV4Training](https://www.hrv4training.com) recovery data to AI assistants, enabling conversational analysis of performance, wellness and training load.

---

## The Problem

Endurance athletes generate rich, multi-dimensional data — training load, power output, heart rate, sleep quality, HRV, subjective wellness — spread across multiple platforms. Extracting meaningful insight from that data typically requires manually exporting files, writing queries or navigating platform-specific dashboards.

Asking a question like *"Was my power output higher on days when my HRV was elevated?"* requires joining data from at least two sources, filtering by date and performing a correlation. Work that takes time and domain knowledge to set up correctly.

---

## The Solution

intervals-mcp exposes the intervals.icu REST API and HRV4Training export data as AI-callable tools via the [Model Context Protocol](https://modelcontextprotocol.io/). Connected to an AI assistant, it enables natural language queries across training, wellness and recovery data without writing code or leaving the chat interface.

**Example interactions:**

```
"How has my training load trended over the past 4 weeks?"
"Compare my normalized power on days when HRV was above vs. below my baseline."
"What were my best 20-minute power efforts this month?"
"Show me my wellness context for the week leading up to my last race."
"What activities did I log in the last 30 days and how did RPE trend?"
"How much time did I spend in each heart rate zone on Tuesday's ride?"
```

---

## Key Capabilities

| Capability | Description |
|---|---|
| **Wellness tracking** | Read and write daily wellness entries — HRV, sleep, fatigue, muscle soreness, mood |
| **Activity analysis** | Power curves, HR curves, pace curves, zone distributions, aerobic decoupling |
| **Interval inspection** | Computed intervals, lap stats, best efforts across any stream |
| **HRV integration** | Daily HRV metrics and recovery scores from HRV4Training, correlated with training data |
| **Training search** | Find activities by name, tag, or interval characteristics |
| **Time-series data** | Raw streams — power, HR, cadence, speed, altitude — for any activity |

---

## Architecture

```
AI Assistant (Claude Desktop, Claude Code, etc.)
        │
        ▼
intervals-mcp (FastMCP / stdio)
        │
        ├── intervals.icu REST API
        │       └── Training load, activities, wellness, streams
        │
        └── HRV4Training CSV
                ├── Local directory (direct file read)
                └── Dropbox API (remote fetch, auto token refresh)
```

### Design Decisions

**MCP as the integration layer.** The Model Context Protocol provides a standard interface between AI models and external data sources. Implementing MCP makes this server compatible with any MCP-capable client — Claude Desktop, Claude Code, VS Code, or custom tooling — without modification.

**Domain-separated routers.** Tools are organized into modules by concern (`athlete`, `wellness`, `activities`, `hrv`). This keeps each domain independently testable and makes it straightforward to load only the relevant subset of tools for a given conversation.

**HRV4Training via Dropbox API.** HRV4Training has no public API. Rather than require a manual file sync step, the server integrates with the Dropbox API directly fetching the most recently modified CSV from a designated app folder on demand. A local directory path is also supported for environments with Dropbox desktop sync available.

**Separate server from strava-mcp.** The intervals.icu public API does not proxy Strava-sourced activity data due to Strava's API terms. Raw activity streams, segment efforts and gear data require direct Strava API access. The two servers are designed to run alongside each other. intervals.icu handles training analytics and wellness and strava-mcp handles raw activity data.

**Errors surface as exceptions.** Tool functions raise `RuntimeError` on API failures rather than returning error strings. This ensures the exact API error message reaches the AI assistant rather than being paraphrased.

---

## Technology Stack

| Component | Technology |
|---|---|
| MCP Server | Python, [FastMCP](https://github.com/jlowin/fastmcp) |
| HTTP Client | [httpx](https://www.python-httpx.org) |
| Training Platform | [intervals.icu](https://intervals.icu) REST API |
| HRV Data | [HRV4Training](https://www.hrv4training.com) CSV via Dropbox API or local path |
| Credential Management | python-dotenv with OAuth 2.0 token auto-refresh |
| Runtime | Python 3.11, Conda |

---

## MCP Tools

### Athlete
| Tool | Description |
|---|---|
| `get_athlete` | Get athlete profile and settings |

### Wellness
| Tool | Description |
|---|---|
| `list_wellness` | List wellness entries for a date range |
| `get_wellness` | Get a single wellness entry by date |
| `update_wellness` | Create or update a wellness entry |
| `bulk_update_wellness` | Update multiple wellness records in one call |

### Activities
| Tool | Description |
|---|---|
| `list_activities` | List activities for a date range |
| `search_activities` | Search activities by name or tag (summary) |
| `search_activities_full` | Search activities by name or tag (full objects) |
| `interval_search_activities` | Find activities with intervals matching duration and intensity |
| `get_activities_by_ids` | Fetch multiple activities by ID |
| `get_activity` | Get full details for a single activity |
| `update_activity` | Update activity fields (name, type, RPE, etc.) |
| `delete_activity` | Delete an activity |

### Activity Analysis
| Tool | Description |
|---|---|
| `get_activity_streams` | Time-series data (power, HR, cadence, speed, altitude, etc.) |
| `get_activity_intervals` | Computed intervals and laps |
| `get_activity_interval_stats` | Stats for an arbitrary slice of the activity |
| `get_activity_best_efforts` | Best efforts for a stream (power, HR, pace) |
| `get_activity_power_curve` | Mean-maximal power curve |
| `get_activity_hr_curve` | Mean-maximal heart rate curve |
| `get_activity_pace_curve` | Mean-maximal pace curve |
| `get_activity_power_histogram` | Power distribution histogram |
| `get_activity_hr_histogram` | Heart rate distribution histogram |
| `get_activity_pace_histogram` | Pace distribution histogram |
| `get_activity_power_vs_hr` | Power vs HR data (aerobic decoupling) |
| `get_activity_time_at_hr` | Time in each heart rate zone |
| `get_activity_map` | Route coordinates and bounding box |
| `get_activity_weather` | Weather conditions during the activity |
| `get_activity_segments` | Matched Strava/local segments |
| `get_activity_messages` | List comments on an activity |
| `post_activity_message` | Add a comment to an activity |

### HRV
| Tool | Description |
|---|---|
| `get_hrv_data` | Daily HRV metrics, recovery score, sleep, and subjective wellness from HRV4Training |

---

## Setup

### Prerequisites

- [Conda](https://docs.conda.io/en/latest/miniconda.html)
- An [intervals.icu](https://intervals.icu) account with API access enabled
- (Optional) [HRV4Training](https://www.hrv4training.com) with Dropbox export configured

### Installation

1. Create the conda environment:
    ```bash
    conda env create -f environment.yml
    conda activate intervals-mcp
    ```

2. Configure credentials:
    ```bash
    cp .env.example .env
    ```
    Edit `.env` and fill in your values:
    ```
    INTERVALS_ATHLETE_ID=i12345        # from your profile URL
    INTERVALS_API_KEY=your_key_here    # Settings > Developer Settings
    ```

3. (Optional) Configure HRV4Training — choose one:

    **Option A — Local directory** (e.g. synced via Dropbox desktop app):
    ```
    HRV4TRAINING_CSV_DIR=/path/to/hrv/exports
    ```
    On WSL, Windows paths are accessible at `/mnt/c/Users/yourname/...`. The most recently modified CSV is used automatically.

    **Option B — Dropbox API** (no local sync required):
    Create an app at [dropbox.com/developers](https://www.dropbox.com/developers/apps) with App folder scope and add `http://localhost:8765/callback` as the redirect URI. Then:
    ```
    DROPBOX_APP_KEY=your_app_key
    DROPBOX_APP_SECRET=your_app_secret
    ```
    Run the one-time authorization:
    ```bash
    python auth_dropbox.py
    ```
    Export your HRV4Training CSV into the Dropbox app folder (`Apps/<your-app-name>/`). The server fetches the most recently modified CSV automatically and refreshes tokens as needed.

    > **Running in WSL?** Run `python auth_dropbox.py --code YOUR_CODE` after copying the authorization code from the browser redirect URL.

### Connecting from Claude Desktop (Windows, server running in WSL)

```json
{
  "mcpServers": {
    "intervals": {
      "command": "wsl.exe",
      "args": [
        "/home/yourname/miniconda3/envs/intervals-mcp/bin/python",
        "/home/yourname/code/mcp-servers/intervals-mcp/server.py"
      ]
    }
  }
}
```

### Connecting from Claude Code or Claude Desktop (macOS/Linux)

```json
{
  "mcpServers": {
    "intervals": {
      "command": "/path/to/miniconda3/envs/intervals-mcp/bin/python",
      "args": ["/path/to/mcp-servers/intervals-mcp/server.py"]
    }
  }
}
```

---

## Limitations and Known Constraints

- **Strava activity data is not available through intervals.icu.** The intervals.icu public API does not proxy raw Strava data. For activity streams, segment efforts and gear, use [strava-mcp](../strava-mcp/) alongside this server.
- **HRV4Training has no public API.** Data is sourced from a CSV export. This requires a periodic manual export from the HRV4Training app; it is not a live feed.
- **Write operations are available but unconfirmed.** `update_activity`, `update_wellness` and `delete_activity` write to intervals.icu. Use with care in automated or multi-step agent workflows.
- **Model quality affects analysis depth.** Claude Sonnet 4.6 or later is recommended for reliable tool use and multi-source data correlation. Earlier model versions showed hallucination of training data when tool calls were expected.

---

## Roadmap Considerations

- **Cross-source analysis server** — dedicated MCP server with pre-computed correlations between HRV, sleep and performance metrics (normalized power, HR efficiency, segment times vs. fitness model)
- **Strava integration in a single query** — agent-level orchestration to join intervals.icu and Strava data in a single conversation without switching servers
- **Wellness trend alerting** — tool to flag meaningful deviations in HRV or sleep patterns relative to rolling baseline
- **Live HRV feed** — integration with wearables that offer a direct API (Garmin, Polar, Whoop) to eliminate the CSV export step

---

## License

MIT
