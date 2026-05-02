# mcp-servers

A collection of [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) servers built with [FastMCP](https://github.com/jlowin/fastmcp).

## Servers

| Server | Description |
|---|---|
| [intervals-mcp](intervals-mcp/) | Tools for the [intervals.icu](https://intervals.icu) training and wellness platform — activities, wellness metrics, power curves, and more |
| [strava-mcp](strava-mcp/) | Tools for the [Strava](https://www.strava.com) fitness platform — activity data, laps, streams, zones, and athlete stats |
| [mqtt-mcp](mqtt-mcp/) | Tools for exploring an MQTT broker — topic discovery, subtopic navigation, and value inspection |
| [opcua-mcp](opcua-mcp/) | Tools for browsing and reading OPC-UA servers — node discovery, metadata inspection, and live value reads. Includes a Water Treatment Plant simulator |

## Structure

Each server lives in its own subdirectory with:
- `server.py` — the MCP server implementation
- `environment.yml` — conda environment definition
- `requirements.txt` — pip dependencies
- `.env.example` — required environment variables
- `README.md` — setup and usage instructions

## License

MIT
