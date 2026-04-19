# intervals-mcp

An [MCP](https://modelcontextprotocol.io/) server for the [intervals.icu](https://intervals.icu) training and wellness platform. Exposes the intervals.icu REST API as tools so AI agents can read and analyse training data, wellness metrics, and activity details.

## Tools

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
| `get_hrv_data` | Daily HRV metrics, recovery score, sleep, and subjective wellness from HRV4Training CSV export |

## Setup

### Prerequisites

- [Conda](https://docs.conda.io/en/latest/miniconda.html)
- An intervals.icu account with API access enabled
- (Optional) [HRV4Training](https://www.hrv4training.com) with CSV export to a local folder

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

3. (Optional) Configure HRV4Training:
    Export your measurements from HRV4Training to a local folder, then set the directory in `.env`:
    ```
    HRV4TRAINING_CSV_DIR=/path/to/hrv/exports
    ```
    The most recently modified CSV in that directory is used automatically — no need to update the path after each export. On WSL, Windows paths are accessible at `/mnt/c/Users/yourname/...`.

## Usage

Run the server over stdio:
```bash
conda activate intervals-mcp
python server.py
```

### Connecting from Claude Code

Add the server to your MCP config (`.claude/settings.json` or `~/.claude.json`):

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

### Connecting from Claude Desktop (macOS/Linux)

Add to `claude_desktop_config.json`:

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

### Connecting from Claude Desktop (Windows, server running in WSL)

Use `wsl.exe` to invoke the server across the WSL boundary:

```json
{
  "mcpServers": {
    "intervals": {
      "command": "wsl.exe",
      "args": [
        "/home/seanslavin/miniconda3/envs/intervals-mcp/bin/python",
        "/home/seanslavin/code/mcp-servers/intervals-mcp/server.py"
      ]
    }
  }
}
```

`wsl.exe` is on the Windows `PATH` by default. The `.env` file is loaded relative to `server.py`, so credentials are picked up automatically.
