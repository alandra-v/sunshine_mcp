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
