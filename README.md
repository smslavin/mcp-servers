# mcp-servers

A collection of [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) servers built with [FastMCP](https://github.com/jlowin/fastmcp).

## Servers

| Server | Description |
|---|---|
| [intervals-mcp](intervals-mcp/) | Tools for the [intervals.icu](https://intervals.icu) training and wellness platform — activities, wellness metrics, power curves, and more |
| [mqtt-mcp](mqtt-mcp/) | Tools for exploring an MQTT broker — topic discovery, subtopic navigation, and value inspection |

## Structure

Each server lives in its own subdirectory with:
- `server.py` — the MCP server implementation
- `environment.yml` — conda environment definition
- `requirements.txt` — pip dependencies
- `.env.example` — required environment variables
- `README.md` — setup and usage instructions

## License

MIT
