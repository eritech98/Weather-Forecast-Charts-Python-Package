#!/usr/bin/env python3
"""
Basic usage examples for weather-charts package.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_api_key():
    """Get API key from .env or prompt user."""
    api_key = os.getenv('OPENWEATHER_API_KEY')
    if not api_key:
        print("OPENWEATHER_API_KEY not found in .env file")
        print("Please enter your OpenWeatherMap API key:")
        api_key = input("API Key: ").strip()
        if not api_key:
            print("No API key provided. Exiting.")
            sys.exit(1)
    return api_key

def example_1_basic_chart():
    """Example 1: Generate a basic temperature chart."""
    print("\n" + "=" * 60)
    print("EXAMPLE 1: Basic Temperature Chart")
    print("=" * 60)
    
    from weather_charts import WeatherCharts
    
    api_key = get_api_key()
    weather = WeatherCharts(api_key)
    
    print("Generating temperature chart for Nairobi...")
    result = weather.get_weather_graph(
        location="Nairobi",
        graph_type="temperature",
        days=3,
        units="metric",
        output_format="png"
    )
    
    # Save chart
    with open("nairobi_temperature.png", "wb") as f:
        f.write(result['chart'].read())
    
    print(f"Chart saved as: nairobi_temperature.png")
    print(f"Location: {result['data']['location']['city']}")
    print(f"Data points: {len(result['data']['forecast'])}")
    print(f"Temperature range: {min(f['temperature'] for f in result['data']['forecast']):.1f}°C to {max(f['temperature'] for f in result['data']['forecast']):.1f}°C")

def example_2_multiple_chart_types():
    """Example 2: Generate multiple types of charts."""
    print("\n" + "=" * 60)
    print("EXAMPLE 2: Multiple Chart Types")
    print("=" * 60)
    
    from weather_charts import WeatherCharts
    
    api_key = get_api_key()
    weather = WeatherCharts(api_key)
    
    locations = ["London", "Tokyo", "New York"]
    chart_types = ["temperature", "humidity", "rainfall"]
    
    for location in locations:
        for chart_type in chart_types:
            try:
                filename = f"{location.lower()}_{chart_type}.png"
                print(f"\nGenerating {chart_type} chart for {location}...")
                
                result = weather.get_weather_graph(
                    location=location,
                    graph_type=chart_type,
                    days=2,
                    output_format="png"
                )
                
                with open(filename, "wb") as f:
                    f.write(result['chart'].read())
                
                print(f"   Saved as: {filename}")
                
            except Exception as e:
                print(f"    Failed for {location}/{chart_type}: {str(e)[:50]}")

def example_3_custom_options():
    """Example 3: Using custom options."""
    print("\n" + "=" * 60)
    print("EXAMPLE 3: Custom Chart Options")
    print("=" * 60)
    
    from weather_charts import WeatherCharts
    
    api_key = get_api_key()
    
    # Custom options for WeatherCharts
    weather = WeatherCharts(api_key, options={
        'figsize': (14, 7),
        'style': 'seaborn-v0_8-darkgrid',
        'width': 1200,
        'height': 600
    })
    
    print("Generating composite chart with custom options...")
    result = weather.get_weather_graph(
        location="Paris",
        graph_type="composite",
        days=5,
        units="metric",
        output_format="png",
        show_min_max=True,
        title="Paris Weather Forecast"
    )
    
    with open("paris_composite_custom.png", "wb") as f:
        f.write(result['chart'].read())
    
    print(f"Custom chart saved as: paris_composite_custom.png")

def example_4_coordinates():
    """Example 4: Using coordinates instead of city name."""
    print("\n" + "=" * 60)
    print("EXAMPLE 4: Using Coordinates")
    print("=" * 60)
    
    from weather_charts import WeatherCharts
    
    api_key = get_api_key()
    weather = WeatherCharts(api_key)
    
    # Coordinates for Sydney, Australia
    sydney_coords = {"lat": -33.8688, "lon": 151.2093}
    
    print("Generating wind chart for Sydney using coordinates...")
    result = weather.get_weather_graph(
        location=sydney_coords,
        graph_type="wind",
        days=3,
        output_format="png",
        show_direction=True
    )
    
    with open("sydney_wind_coords.png", "wb") as f:
        f.write(result['chart'].read())
    
    print(f"Chart saved as: sydney_wind_coords.png")
    print(f"Coordinates: {sydney_coords['lat']}, {sydney_coords['lon']}")
    print(f"Resolved to: {result['data']['location']['city']}")

def example_5_raw_data():
    """Example 5: Getting raw weather data without chart."""
    print("\n" + "=" * 60)
    print("EXAMPLE 5: Raw Weather Data")
    print("=" * 60)
    
    from weather_charts import WeatherCharts
    
    api_key = get_api_key()
    weather = WeatherCharts(api_key)
    
    print("Fetching raw weather data for Berlin...")
    data = weather.get_weather_data("Berlin", days=2, units="metric")
    
    print(f" Location: {data['location']['city']}, {data['location']['country']}")
    print(f"Forecast entries: {len(data['forecast'])}")
    print(f"Forecast period: {data['forecast'][0]['datetime']} to {data['forecast'][-1]['datetime']}")
    
    # Print first 3 forecasts
    print("\nFirst 3 forecast entries:")
    for i, forecast in enumerate(data['forecast'][:3]):
        print(f"  {i+1}. {forecast['datetime'].strftime('%a %H:%M')}: "
              f"{forecast['temperature']}°C, "
              f"{forecast['humidity']}% humidity, "
              f"{forecast['wind_speed']} m/s wind")

def example_6_convenience_function():
    """Example 6: Using the convenience function."""
    print("\n" + "=" * 60)
    print("EXAMPLE 6: Convenience Function")
    print("=" * 60)
    
    from weather_charts import get_weather_graph
    
    api_key = get_api_key()
    
    print("Using get_weather_graph() convenience function...")
    result = get_weather_graph(
        location="Dubai",
        api_key=api_key,
        graph_type="humidity",
        days=4,
        output_format="png"
    )
    
    with open("dubai_humidity_convenience.png", "wb") as f:
        f.write(result['chart'].read())
    
    print(f"Chart saved as: dubai_humidity_convenience.png")
    print(f"Metadata: {result['metadata']['graph_type']} chart generated at {result['metadata']['generated_at']}")

def main():
    """Run all examples."""
    print("Weather Charts Package - Examples")
    print("=" * 60)
    
    # Check if API key is available
    api_key = os.getenv('OPENWEATHER_API_KEY')
    if not api_key:
        print("Note: OPENWEATHER_API_KEY not found in .env")
        print("You'll be prompted for it when needed.")
    else:
        print(f"API key loaded from .env")
    
    # Run examples
    examples = [
        example_1_basic_chart,
        example_2_multiple_chart_types,
        example_3_custom_options,
        example_4_coordinates,
        example_5_raw_data,
        example_6_convenience_function
    ]
    
    for i, example in enumerate(examples, 1):
        try:
            example()
        except KeyboardInterrupt:
            print("\n\nExample interrupted by user")
            break
        except Exception as e:
            print(f"\nExample {i} failed: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("All examples completed!")
    print("=" * 60)
    print("\n Generated files:")
    
    # List generated PNG files
    import glob
    png_files = glob.glob("*.png")
    if png_files:
        for file in sorted(png_files):
            size = os.path.getsize(file)
            print(f" {file} ({size:,} bytes)")
    else:
        print("  No PNG files generated (check for errors)")
    
    print("\n Examples completed successfully!")

if __name__ == "__main__":
    main()