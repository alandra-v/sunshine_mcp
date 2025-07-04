import json
import asyncio
import click
from .sunshine_finder import SunshineFinder
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
