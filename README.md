# mcp-servers

A collection of [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) servers built with [FastMCP](https://github.com/jlowin/fastmcp).

## Servers

| Server | Description |
|---|---|
| [intervals-mcp](intervals-mcp/) | Tools for the [intervals.icu](https://intervals.icu) training and wellness platform — activities, wellness metrics, power curves, and more |
| [strava-mcp](strava-mcp/) | Tools for the [Strava](https://www.strava.com) fitness platform — activity data, laps, streams, zones, and athlete stats |
| [analytics-mcp](analytics-mcp/) | Cross-source analytics joining intervals.icu and Strava — HRV vs performance, fitness vs segment times, training load vs sleep |

The MQTT and OPC-UA servers moved to their own repos, with their history, so each can be versioned and tagged: [smslavin/mqtt-mcp](https://github.com/smslavin/mqtt-mcp) and [smslavin/opcua-mcp](https://github.com/smslavin/opcua-mcp).

## Structure

Each server lives in its own subdirectory with:
- `server.py` — the MCP server implementation
- `environment.yml` — conda environment definition
- `requirements.txt` — pip dependencies
- `.env.example` — required environment variables
- `README.md` — setup and usage instructions

## License

MIT
