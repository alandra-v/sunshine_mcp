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
A complete sunshine finder CLI tool that:
1. **Gets current location** using CoreLocationCLI (macOS system tool)
2. **Fetches real-time weather data** from Met.no API
3. **Calculates weather scores** based on temperature, cloud coverage, precipitation, and wind
4. **Searches in configurable radius** (default 100km) using concentric circles
5. **Ranks locations** by weather quality and presents top 5 results

### Key Architecture Decisions
- **Async/await pattern** for efficient API calls
- **Dataclasses** for clean data structures (`WeatherData`, `Location`)
- **Click framework** for professional CLI interface
- **Modular design** with separate `SunshineFinder` class
- **Error handling** with graceful degradation
- **JSON output option** for composability with other tools

### Weather Scoring Algorithm
Smart scoring system (0-100) that weights:
- **Temperature** (30%): Optimal around 22.5°C
- **Cloud coverage** (40%): Less clouds = higher score
- **Precipitation** (20%): No rain preferred
- **Wind speed** (10%): Moderate wind acceptable

### Usage Examples
```bash
# Default search (100km radius)
uv run python main.py

# Custom radius
uv run python main.py --radius 50

# JSON output for integration
uv run python main.py --json-output
```

---

## 🔧 Technical Notes

### Dependencies
- `httpx`: Modern async HTTP client
- `click`: Professional CLI framework
- `subprocess`: For CoreLocationCLI integration
- `asyncio`: Async/await support

### API Limitations
- Met.no API has rate limits (check their terms)
- CoreLocationCLI requires macOS and location permissions
- Weather data accuracy depends on API provider

### Error Handling
- Graceful degradation when locations fail
- Clear error messages for debugging
- Fallback mechanisms for API failures

### Performance
- Concurrent API calls for multiple locations
- Efficient circle generation algorithm
- Minimal memory footprint with dataclasses
