# Roadmap

Planned additions and fixes to the mcp-servers collection, organized by phase.

---

## Phase 0 — Architecture fixes (MCP spec compliance)

Findings from a review against the MCP specification (modelcontextprotocol.io). Address these before building new features.

### High priority

#### Thread safety — race condition on shared state in mqtt-mcp

**File:** `mqtt-mcp/server.py`

`topic_tree` and `topic_values` are module-level dicts mutated by the paho MQTT callback thread (via `loop_start()`) while tool functions read them from the main thread. No locks. Fix by wrapping all mutations and reads in a `threading.Lock`.

#### Fix stdout logging in mqtt-mcp

**File:** `mqtt-mcp/server.py`

`on_message` prints errors to stdout. For any server using stdio transport, stdout is the JSON-RPC channel — writing to it corrupts the stream. Change all `print(...)` calls to `print(..., file=sys.stderr)`.

#### Raise on JSON decode errors instead of returning error strings

**Files:** `intervals-mcp/routers/wellness.py`, `strava-mcp/routers/activities.py`

`update_wellness`, `bulk_update_wellness`, and `update_activity` (strava) catch `json.JSONDecodeError` and return a plain string. The MCP client sees `isError: false` with error text in the content — the tool appears to succeed. These should raise so FastMCP sets `isError: true` on the tool result.

```python
# fix
except json.JSONDecodeError as e:
    raise ValueError(f"Invalid JSON payload: {e}")
```

#### Replace untyped `payload: str` parameters with typed parameters or Pydantic models

**Files:** `intervals-mcp/routers/wellness.py`, `intervals-mcp/routers/activities.py`, `strava-mcp/routers/activities.py`

`update_wellness`, `bulk_update_wellness`, `update_activity`, and `post_activity_message` accept a raw JSON string. FastMCP generates `{"type": "string"}` in the input schema — the LLM gets no type information for the fields inside. Replace with explicit optional parameters (for tools with a small, fixed field set) or a Pydantic model (for tools with a wide field set like wellness).

---

### Medium priority

#### `scan_topics` blocks the server for its full duration

**File:** `mqtt-mcp/server.py`

`scan_topics` calls `time.sleep(duration_seconds)` (default 10s) in a sync tool function, freezing the server for the caller's entire wait. Cap the maximum allowed duration and document it as a known limitation in the tool description.

#### Tool functions return plain error strings as successful results in mqtt-mcp

**File:** `mqtt-mcp/server.py`

`list_topics`, `list_subtopics`, and `read_topic_value` return strings like `"No topics discovered yet"` and `"Topic not found"` as normal return values — `isError: false` with error text. Same issue as intervals/strava. These should raise so FastMCP sets `isError: true`.

#### `browse_tree` silently drops subtrees on error in opcua-mcp

**File:** `opcua-mcp/server.py`

When `node.get_children()` raises, the entire subtree is silently omitted from the result. The caller receives a partial tree with no indication it's incomplete. Append a warning line to `lines` before returning so the gap is visible.

#### Move inline imports to top of file

**Files:** `strava-mcp/routers/gear.py`, `strava-mcp/routers/segments.py`, `strava-mcp/routers/routes.py`, `opcua-mcp/server.py`

`import json`, `from datetime import ...`, and `from opcua_discover import discover` appear inside function bodies. Move to module level.

#### Consolidate sequential HTTP requests into one client context

**Files:** `strava-mcp/routers/athlete.py` (`get_athlete_stats`), `strava-mcp/routers/routes.py` (`list_routes`)

Both functions open two separate `httpx.Client` contexts to make sequential requests to the same host. Reuse a single client context for both requests.

---

### Low priority

#### Fix misleading `get_athlete_stats` docstring

**File:** `strava-mcp/routers/athlete.py`

Docstring says "Requires the athlete ID from get_athlete." The function fetches the ID internally — the LLM may unnecessarily call `get_athlete` first. Remove that sentence.

#### Remove dead `handle_response` call in `get_athlete_stats`

**File:** `strava-mcp/routers/athlete.py`

`handle_response(r)` is called on the first response but its return value is discarded. The call is only for the error-raising side effect. Restructure to reuse one client context (see above) and call `handle_response` only on the final response.

#### Stale OPC-UA connection not detected in opcua-mcp

**File:** `opcua-mcp/server.py`

After an OPC-UA server drop, `_client` remains non-None. `_require_client()` returns the stale client and the next tool call gets a cryptic asyncua error instead of "not connected." Add a liveness check or catch the error, clear `_client`, and re-raise with a clear message.

#### MQTT connection failure is silent

**File:** `mqtt-mcp/server.py`

`start_mqtt()` is called at module import. If the broker is unreachable, the server starts with an empty topic tree and no indication anything is wrong. Surface the failure through stderr logging at minimum.

#### Scan state bleeds into global topic tree in mqtt-mcp

**File:** `mqtt-mcp/server.py`

`scan_topics` adds a per-filter callback but the global `on_message` (subscribed to `MQTT_TOPIC_ROOT`) still fires for the same messages, updating the persistent `topic_tree`. Scan results and persistent subscription state are not isolated.

---

## Phase 1 — Self-contained additions to existing servers

### intervals-mcp: `wellness_trend_alert`

New tool in `routers/wellness.py`.

Fetches a rolling window of wellness entries and computes a baseline (mean ± std) for a given metric. Flags whether the current reading is a meaningful deviation — useful for surfacing early signs of overtraining, illness, or recovery.

**Parameters**
| Parameter | Description |
|---|---|
| `metric` | Wellness field to analyse: `hrv_rmssd`, `sleep_score`, `fatigue`, `muscle_soreness`, `mood`, etc. |
| `window_days` | Number of days to include in the rolling baseline (default: 28) |
| `threshold_stddevs` | How many standard deviations from the mean constitutes a flag (default: 1.5) |

---

### strava-mcp: `get_gear_maintenance_status`

New tool in `routers/gear.py`.

Pulls all gear (bikes and shoes) with their cumulative logged distance. Accepts per-type distance thresholds and returns a maintenance status report — flagging any gear that is approaching or has exceeded the threshold.

**Parameters**
| Parameter | Description |
|---|---|
| `thresholds` | JSON object mapping gear type to distance threshold in km, e.g. `{"bike": 3000, "shoes": 800}` |

---

## Phase 2 — New `analytics-mcp` server

A dedicated cross-source analytics server that joins data from intervals.icu (training load, wellness, HRV) and Strava (activity streams, segment efforts) in a single tool call. Neither existing server can do this alone: intervals.icu's public API does not proxy Strava data, and strava-mcp has no access to the fitness model.

**Location:** `analytics-mcp/`  
**Credentials:** own `.env` holding both intervals.icu and Strava credentials

### Tools

#### `correlate_hrv_with_performance`

For a given date range, fetches daily HRV from intervals.icu wellness and pairs each day with the normalized power and HR efficiency from any activity logged that day. Returns a summary table and Pearson correlation coefficient.

#### `fitness_vs_segment_prs`

Pulls all of the athlete's efforts on a given Strava segment, then looks up CTL, ATL and TSB from intervals.icu for each effort date. Returns a table suitable for evaluating whether the fitness model predicts segment performance.

#### `training_load_vs_sleep`

Joins ATL/CTL from the intervals.icu fitness model with the wellness sleep score over a date range. Surfaces patterns between accumulated load and sleep quality — useful for identifying the lag between hard training blocks and sleep degradation.

---

## Out of scope (by decision)

| Item | Reason |
|---|---|
| Live HRV feed (Garmin, Polar, Whoop) | Skipped — current CSV/Dropbox workflow is sufficient |
| Multi-athlete support | Skipped — single-athlete use case |
