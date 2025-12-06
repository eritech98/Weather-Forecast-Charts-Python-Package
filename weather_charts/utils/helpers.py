#!/usr/bin/env python3
"""
Basic usage example for weather-charts package.
"""

import os
from weather_charts import WeatherCharts, get_weather_graph

def main():
    # Get API key from environment variable
    api_key = os.getenv('OPENWEATHER_API_KEY')
    if not api_key:
        print("Please set OPENWEATHER_API_KEY environment variable")
        print("You can get a free API key from: https://openweathermap.org/api")
        return
    
    # Initialize with API key
    print("Initializing WeatherCharts...")
    weather = WeatherCharts(api_key, options={
        'figsize': (12, 6),
        'style': 'seaborn-v0_8-darkgrid'
    })
    
    # Example 1: Get temperature chart for Nairobi
    print("\n1. Getting temperature chart for Nairobi...")
    try:
        result = weather.get_weather_graph(
            location="Nairobi",
            graph_type="temperature",
            days=3,
            units="metric",
            output_format="png"
        )
        
        # Save the chart
        with open("nairobi_temperature.png", "wb") as f:
            f.write(result["chart"].read())
        
        print(f"✓ Chart saved as: nairobi_temperature.png")
        print(f"✓ Location: {result['data']['location']['city']}, {result['data']['location']['country']}")
        print(f"✓ Forecast points: {len(result['data']['forecast'])}")
        
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Example 2: Get humidity chart for London
    print("\n2. Getting humidity chart for London...")
    try:
        result = weather.get_weather_graph(
            location="London",
            graph_type="humidity",
            days=5,
            output_format="png"
        )
        
        with open("london_humidity.png", "wb") as f:
            f.write(result["chart"].read())
        
        print(f"✓ Chart saved as: london_humidity.png")
        
        # Display some statistics
        humidities = [entry['humidity'] for entry in result['data']['forecast']]
        avg_humidity = sum(humidities) / len(humidities)
        print(f"✓ Average humidity: {avg_humidity:.1f}%")
        
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Example 3: Get composite chart for New York
    print("\n3. Getting composite chart for New York...")
    try:
        result = weather.get_weather_graph(
            location={"lat": 40.7128, "lon": -74.0060},  # NYC coordinates
            graph_type="composite",
            days=2,
            output_format="png"
        )
        
        with open("new_york_composite.png", "wb") as f:
            f.write(result["chart"].read())
        
        print(f"✓ Chart saved as: new_york_composite.png")
        
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Example 4: Using the convenience function
    print("\n4. Using convenience function for Tokyo...")
    try:
        result = get_weather_graph(
            location="Tokyo",
            api_key=api_key,
            graph_type="rainfall",
            days=4,
            output_format="png"
        )
        
        with open("tokyo_rainfall.png", "wb") as f:
            f.write(result["chart"].read())
        
        print(f"✓ Chart saved as: tokyo_rainfall.png")
        
        # Calculate total rainfall
        total_rain = sum(entry['rainfall'] for entry in result['data']['forecast'])
        print(f"✓ Total forecast rainfall: {total_rain:.1f} mm")
        
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Example 5: Get raw weather data
    print("\n5. Getting raw weather data for Paris...")
    try:
        data = weather.get_weather_data("Paris", days=2)
        
        print(f"✓ Location: {data['location']['city']}")
        print(f"✓ Current temperature: {data['forecast'][0]['temperature']}°C")
        print(f"✓ Weather description: {data['forecast'][0]['description']}")
        print(f"✓ Wind speed: {data['forecast'][0]['wind_speed']} m/s")
        
    except Exception as e:
        print(f"✗ Error: {e}")
    
    print("\n" + "="*50)
    print("All examples completed!")
    print("Check the generated PNG files in the current directory.")

if __name__ == "__main__":
    main()