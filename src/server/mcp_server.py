#!/usr/bin/env python3

from fastmcp import FastMCP
from ..tools.sunshine_finder import SunshineFinder
import asyncio
from typing import Dict, Any


mcp = FastMCP(
    name="sunshine-finder",
    instructions="A server that helps find locations with good weather/sunshine within a specified radius"
)

finder = SunshineFinder()


@mcp.tool
async def find_sunshine(radius_km: int = 100) -> Dict[str, Any]:
    """
    Find the best sunshine locations within a specified radius.
    
    Args:
        radius_km: Search radius in kilometers (default: 100)
        
    Returns:
        Dictionary containing current location, best locations, and total checked
    """
    return await finder.find_sunshine(radius_km)


@mcp.tool
async def get_weather_at_location(lat: float, lon: float) -> Dict[str, Any]:
    """
    Get weather data and score for a specific location.
    
    Args:
        lat: Latitude coordinate
        lon: Longitude coordinate
        
    Returns:
        Dictionary containing location, weather data, and weather score
    """
    return await finder.get_weather_at_location(lat, lon)


@mcp.tool
def get_current_location() -> Dict[str, float]:
    """
    Get the current location using system tools.
    
    Returns:
        Dictionary containing current latitude and longitude
    """
    try:
        lat, lon = finder.get_current_location()
        return {"lat": lat, "lon": lon}
    except Exception as e:
        raise Exception(f"Failed to get current location: {e}")


def main():
    """Main entry point for the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()