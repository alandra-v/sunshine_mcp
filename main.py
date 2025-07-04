import subprocess
import json
import asyncio
from typing import Tuple, List, Dict, Any
from dataclasses import dataclass
import math
import click
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
    # api request and headers
    def __init__(self):
        self.weather_api_url = "https://api.met.no/weatherapi/locationforecast/2.0/compact"

    
    # get location with CoreLocationCLI
    def get_current_location(self) -> Tuple[float, float]: #lat, lon
        """Get current location using CoreLocationCLI"""
        try:
            result = subprocess.run(
                # command to get location
                ["CoreLocationCLI", "-once", "-format", "%latitude %longitude"],
                # return output
                capture_output=True,
                # right click on run go to definition
                text=True,
                check=True
            )
            lat_str, lon_str = result.stdout.strip().split()
            return float(lat_str), float(lon_str)
            # ausbaufähig
        except (subprocess.CalledProcessError, ValueError, FileNotFoundError) as e:
            raise Exception(f"Failed to get current location: {e}")
    
    async def get_weather_data(self, lat: float, lon: float) -> WeatherData:
        # this is a doc string
        """Fetch weather data from Met.no API"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    self.weather_api_url,
                    params={"lat": lat, "lon": lon},
                )
                response.raise_for_status()
                data = response.json()
                
                # Extract current weather data
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
        # Temperature score (optimal around 20-25°C)
        temp_score = 100 - abs(weather.temperature - 22.5) * 4
        temp_score = max(0, min(100, temp_score))
        
        # Cloud coverage score (less clouds = better)
        cloud_score = 100 - weather.cloud_coverage
        
        # Precipitation score (no rain = better)
        precip_score = 100 - (weather.precipitation * 20)
        precip_score = max(0, min(100, precip_score))
        
        # Wind score (moderate wind is ok)
        wind_score = 100 - abs(weather.wind_speed - 5) * 5
        wind_score = max(0, min(100, wind_score))
        
        # Weighted average
        total_score = (temp_score * 0.3 + cloud_score * 0.4 + 
                      precip_score * 0.2 + wind_score * 0.1)
        
        return round(total_score, 1)
    
    def generate_search_locations(self, center_lat: float, center_lon: float, 
                                radius_km: int = 100, num_points: int = 16) -> List[Location]:
        """Generate search locations in a circle around the center"""
        locations = []
        
        # Add center location
        locations.append(Location(center_lat, center_lon, "Current Location", 0))
        
        # Generate points in concentric circles
        for radius in [25, 50, 75, 100]:
            if radius > radius_km:
                break
                
            points_in_circle = max(4, num_points // 4)
            for i in range(points_in_circle):
                angle = (2 * math.pi * i) / points_in_circle
                
                # Convert to approximate lat/lon offset
                lat_offset = (radius / 111) * math.cos(angle)  # ~111 km per degree
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
            # Get current location
            current_lat, current_lon = self.get_current_location()
            click.echo(f"Current location: {current_lat:.4f}, {current_lon:.4f}")
            
            # Generate search locations
            locations = self.generate_search_locations(current_lat, current_lon, radius_km)
            
            # Check weather for each location
            results = []
            click.echo(f"Checking weather at {len(locations)} locations...")
            
            for i, location in enumerate(locations):
                try:
                    weather = await self.get_weather_data(location.lat, location.lon)
                    score = self.calculate_weather_score(weather)
                    
                    results.append({
                        "location": location,
                        "weather": weather,
                        "score": score
                    })
                    
                    click.echo(f"  {i+1}/{len(locations)}: {location.name} - Score: {score}")
                    
                except Exception as e:
                    click.echo(f"  {i+1}/{len(locations)}: {location.name} - Error: {e}")
            
            # Sort by score
            results.sort(key=lambda x: x["score"], reverse=True)
            
            return {
                "current_location": {"lat": current_lat, "lon": current_lon},
                "best_locations": results[:5], # Top 5 results
                "total_checked": len(results)
            }
            
        except Exception as e:
            raise Exception(f"Error in find_sunshine: {e}")


# maybe put cli logic somewhere else
@click.command()
@click.option("--radius", default=100, help="Search radius in kilometers")
# good to have json output for composibility
@click.option("--json-output", is_flag=True, help="Output results as JSON")
# add more commands like above if wanted (also add in main())

def main(radius: int, json_output: bool):
    """Find locations with good weather/sunshine within a specified radius."""
    finder = SunshineFinder()
    
    try:
        # to "await" running in asyncio
        results = asyncio.run(finder.find_sunshine(radius))
        
        if json_output:
            click.echo(json.dumps(results, indent=2, default=str))
        else:
            click.echo("\n🌞 Sunshine Finder Results 🌞")
            click.echo("=" * 40)
            
            current = results["current_location"]
            click.echo(f"Current Location: {current['lat']:.4f}, {current['lon']:.4f}")
            click.echo(f"Locations checked: {results['total_checked']}")
            
            click.echo("\n🏆 Top 5 Best Weather Locations:")
            for i, result in enumerate(results["best_locations"][:5], 1):
                loc = result["location"]
                weather = result["weather"]
                score = result["score"]
                
                click.echo(f"\n{i}. {loc.name} (Score: {score}/100)")
                click.echo(f"   📍 {loc.lat:.4f}, {loc.lon:.4f}")
                if loc.distance_km > 0:
                    click.echo(f"   📏 Distance: {loc.distance_km}km")
                click.echo(f"   🌡️  Temperature: {weather.temperature}°C")
                click.echo(f"   ☁️  Cloud coverage: {weather.cloud_coverage}%")
                click.echo(f"   🌧️  Precipitation: {weather.precipitation}mm")
                click.echo(f"   💨 Wind speed: {weather.wind_speed}m/s")
    
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        exit(1)

# if you want to run this from the terminal u need this
if __name__ == "__main__":
    main()
