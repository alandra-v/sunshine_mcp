import subprocess
import asyncio
from typing import Tuple, List, Dict, Any
from dataclasses import dataclass
import math
import httpx


@dataclass
class WeatherData:
    temperature: float
    cloud_coverage: float
    precipitation: float
    wind_speed: float
    timestamp: str


@dataclass
class Location:
    lat: float
    lon: float
    name: str
    distance_km: float = 0.0


class SunshineFinder:
    def __init__(self):
        self.weather_api_url = "https://api.met.no/weatherapi/locationforecast/2.0/compact"

    def get_current_location(self) -> Tuple[float, float]:
        """Get current location using CoreLocationCLI"""
        try:
            result = subprocess.run(
                ["CoreLocationCLI", "-once", "-format", "%latitude %longitude"],
                capture_output=True,
                text=True,
                check=True
            )
            lat_str, lon_str = result.stdout.strip().split()
            return float(lat_str), float(lon_str)
        except (subprocess.CalledProcessError, ValueError, FileNotFoundError) as e:
            raise Exception(f"Failed to get current location: {e}")

    async def get_weather_data(self, lat: float, lon: float) -> WeatherData:
        """Fetch weather data from Met.no API"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    self.weather_api_url,
                    params={"lat": lat, "lon": lon},
                )
                response.raise_for_status()
                data = response.json()
                
                current = data["properties"]["timeseries"][0]["data"]["instant"]["details"]
                
                return WeatherData(
                    temperature=current.get("air_temperature", 0),
                    cloud_coverage=current.get("cloud_area_fraction", 100),
                    precipitation=current.get("precipitation_amount", 0),
                    wind_speed=current.get("wind_speed", 0),
                    timestamp=data["properties"]["timeseries"][0]["time"]
                )
            except Exception as e:
                raise Exception(f"Failed to fetch weather data: {e}")

    def calculate_weather_score(self, weather: WeatherData) -> float:
        """Calculate a weather score (0-100, higher is better)"""
        temp_score = 100 - abs(weather.temperature - 22.5) * 4
        temp_score = max(0, min(100, temp_score))
        
        cloud_score = 100 - weather.cloud_coverage
        
        precip_score = 100 - (weather.precipitation * 20)
        precip_score = max(0, min(100, precip_score))
        
        wind_score = 100 - abs(weather.wind_speed - 5) * 5
        wind_score = max(0, min(100, wind_score))
        
        total_score = (temp_score * 0.3 + cloud_score * 0.4 + 
                      precip_score * 0.2 + wind_score * 0.1)
        
        return round(total_score, 1)

    def generate_search_locations(self, center_lat: float, center_lon: float, 
                                radius_km: int = 100, num_points: int = 16) -> List[Location]:
        """Generate search locations in a circle around the center"""
        locations = []
        
        locations.append(Location(center_lat, center_lon, "Current Location", 0))
        
        for radius in [25, 50, 75, 100]:
            if radius > radius_km:
                break
                
            points_in_circle = max(4, num_points // 4)
            for i in range(points_in_circle):
                angle = (2 * math.pi * i) / points_in_circle
                
                lat_offset = (radius / 111) * math.cos(angle)
                lon_offset = (radius / (111 * math.cos(math.radians(center_lat)))) * math.sin(angle)
                
                new_lat = center_lat + lat_offset
                new_lon = center_lon + lon_offset
                
                locations.append(Location(
                    new_lat, new_lon, 
                    f"{radius}km {['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'][i % 8]}", 
                    radius
                ))
        
        return locations

    async def find_sunshine(self, radius_km: int = 100) -> Dict[str, Any]:
        """Main function to find the best sunshine location"""
        try:
            current_lat, current_lon = self.get_current_location()
            
            locations = self.generate_search_locations(current_lat, current_lon, radius_km)
            
            results = []
            
            for location in locations:
                try:
                    weather = await self.get_weather_data(location.lat, location.lon)
                    score = self.calculate_weather_score(weather)
                    
                    results.append({
                        "location": location,
                        "weather": weather,
                        "score": score
                    })
                    
                except Exception as e:
                    continue
            
            results.sort(key=lambda x: x["score"], reverse=True)
            
            return {
                "current_location": {"lat": current_lat, "lon": current_lon},
                "best_locations": results[:5],
                "total_checked": len(results)
            }
            
        except Exception as e:
            raise Exception(f"Error in find_sunshine: {e}")

    async def get_weather_at_location(self, lat: float, lon: float) -> Dict[str, Any]:
        """Get weather data for a specific location"""
        try:
            weather = await self.get_weather_data(lat, lon)
            score = self.calculate_weather_score(weather)
            
            return {
                "location": {"lat": lat, "lon": lon},
                "weather": {
                    "temperature": weather.temperature,
                    "cloud_coverage": weather.cloud_coverage,
                    "precipitation": weather.precipitation,
                    "wind_speed": weather.wind_speed,
                    "timestamp": weather.timestamp
                },
                "score": score
            }
        except Exception as e:
            raise Exception(f"Error getting weather at location: {e}")