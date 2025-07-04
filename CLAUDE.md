# Sunshine Finder Tool

## Project Goal
Create a tool that helps find locations with good weather/sunshine within a reasonable distance.

## Requirements
- Use Python with `uv` for package management
- Get current location using system tools
- Search for good weather within 100km radius
- Use weather API to check conditions

## Implementation Steps

### 1. Get Current Location
```bash
CoreLocationCLI -once -format "%latitude,%longitude"
```

### 2. Check Weather API
Use the Met.no Weather API to get current and forecast data:
```
https://api.met.no/weatherapi/locationforecast/2.0/compact?lat=51.5&lon=0
```

### 3. Search Strategy
- Start by checking weather at current location
- Use current latitude and longitude as API parameters
- Expand search radius up to 100km for better weather conditions
- Be creative with the search algorithm

## API Reference
- **Weather API**: Met.no LocationForecast API
- **Format**: `https://api.met.no/weatherapi/locationforecast/2.0/compact?lat={lat}&lon={lon}`
- **Location Service**: CoreLocationCLI for macOS

---

## ✅ Implementation Summary

### What We Built
A complete sunshine finder tool ecosystem with:
1. **Core Tool** (`src/tools/sunshine_finder.py`): Gets current location, fetches weather data, calculates scores, searches in radius
2. **CLI Interface** (`src/tools/cli.py`): Command-line tool with Click framework
3. **MCP Server** (`src/server/mcp_server.py`): FastMCP server exposing tools to LLMs
4. **Proper Package Structure**: Organized with `src/` containing `tools/`, `server/`, `client/` folders

### Key Architecture Decisions
- **Modular design**: Separated CLI logic from core API functionality
- **FastMCP integration**: Exposes tools as MCP server for LLM integration
- **Async/await pattern** for efficient API calls
- **Dataclasses** for clean data structures (`WeatherData`, `Location`)
- **Proper Python packaging** with entry points and build system

### Weather Scoring Algorithm
Smart scoring system (0-100) that weights:
- **Temperature** (30%): Optimal around 22.5°C
- **Cloud coverage** (40%): Less clouds = higher score
- **Precipitation** (20%): No rain preferred
- **Wind speed** (10%): Moderate wind acceptable

### MCP Server Tools
The FastMCP server exposes 3 tools:
1. **`find_sunshine(radius_km)`**: Main sunshine finder functionality
2. **`get_weather_at_location(lat, lon)`**: Get weather for specific coordinates
3. **`get_current_location()`**: Get current system location

### Usage Examples
```bash
# CLI Tool
uv run sunshine-cli --radius 50

# MCP Server
uv run sunshine-server

# MCP Inspector (for testing)
npx @modelcontextprotocol/inspector uv --directory . run sunshine-server
```

---

## 🔧 Technical Implementation

### Project Structure
```
src/
├── tools/
│   ├── sunshine_finder.py  # Core logic
│   └── cli.py             # CLI interface
├── server/
│   └── mcp_server.py      # FastMCP server
└── client/                # Reserved for future client examples
```

### Dependencies
- `httpx`: Modern async HTTP client
- `click`: Professional CLI framework
- `fastmcp`: FastMCP framework for MCP server
- `subprocess`: For CoreLocationCLI integration

### Key Refactoring for MCP
1. **Separated concerns**: Moved CLI-specific code (`click.echo`) out of core logic
2. **Module structure**: Created proper Python package with `__init__.py` files
3. **Entry points**: Added `sunshine-cli` and `sunshine-server` commands
4. **Build system**: Configured hatchling for proper package installation

### MCP Integration Benefits
- **LLM Access**: Tools can be called by Claude, ChatGPT, etc.
- **Standardized Interface**: MCP protocol provides consistent tool calling
- **Testing**: MCP Inspector allows interactive testing and debugging
- **Composability**: Can be combined with other MCP servers

### Error Handling
- Graceful degradation when locations fail
- Clear error messages for debugging
- Fallback mechanisms for API failures
