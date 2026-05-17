# analytics-mcp

A cross-source analytics server that joins [intervals.icu](https://intervals.icu) training load and wellness data with [Strava](https://www.strava.com) activity streams in a single tool call. Neither existing server can do this alone: intervals.icu's public API does not proxy Strava data, and strava-mcp has no access to the fitness model.

Designed to run alongside [intervals-mcp](../intervals-mcp/) and [strava-mcp](../strava-mcp/).

---

## MCP Tools

### Correlations

| Tool | Description |
|---|---|
| `correlate_hrv_with_performance` | Pair daily HRV with same-day normalized power and HR efficiency; return Pearson correlations |
| `training_load_vs_sleep` | Correlate CTL, ATL, and form (TSB) from intervals.icu with daily sleep score |
| `fitness_vs_segment_prs` | Join Strava segment effort times with intervals.icu fitness metrics on each effort date |

**Example interactions:**

```
"Was my normalized power higher on days when my HRV was elevated?"
"How does my sleep quality correlate with my training load over the past 3 months?"
"Does my CTL predict my times on my local climb?"
```

---

## Architecture

```
AI Assistant (Claude Desktop, Claude Code, etc.)
        │
        ▼
analytics-mcp (FastMCP / stdio)
        │
        ├── intervals.icu REST API
        │       └── Wellness (HRV, sleep, CTL, ATL, form)
        │
        └── Strava REST API
                └── Segment efforts
```

---

## Setup

### Prerequisites

- [Conda](https://docs.conda.io/en/latest/miniconda.html)
- An [intervals.icu](https://intervals.icu) account with API access enabled
- A Strava account with an authorized API application (see [strava-mcp setup](../strava-mcp/README.md))

### Installation

1. Create the conda environment:
    ```bash
    conda env create -f environment.yml
    conda activate analytics-mcp
    ```

2. Configure credentials:
    ```bash
    cp .env.example .env
    ```
    Edit `.env` and fill in your intervals.icu credentials. For Strava, copy the token values from your strava-mcp `.env` — they share the same app credentials.

### Connecting from Claude Desktop (Windows, server running in WSL)

```json
{
  "mcpServers": {
    "analytics": {
      "command": "wsl.exe",
      "args": [
        "/home/yourname/miniconda3/envs/analytics-mcp/bin/python",
        "/home/yourname/code/mcp-servers/analytics-mcp/server.py"
      ]
    }
  }
}
```

### Connecting from Claude Code or Claude Desktop (macOS/Linux)

```json
{
  "mcpServers": {
    "analytics": {
      "command": "/path/to/miniconda3/envs/analytics-mcp/bin/python",
      "args": ["/path/to/mcp-servers/analytics-mcp/server.py"]
    }
  }
}
```

---

## Notes

- `training_load_vs_sleep` and `fitness_vs_segment_prs` require that intervals.icu wellness entries include CTL, ATL, and form fields. These are populated when the athlete has training load history in intervals.icu.
- Pearson correlation is computed from stdlib (`statistics` / manual calculation) — no scipy dependency required.
- All three tools require at least 3 paired data points to produce a correlation. Insufficient data returns a plain explanation rather than an error.
