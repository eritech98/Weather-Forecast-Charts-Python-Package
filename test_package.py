#!/usr/bin/env python3
"""Test for Windows without Unicode characters."""

import os
import sys

print("TESTING WEATHER-CHARTS PACKAGE")
print("=" * 60)

# Check current directory
print(f"\nCurrent directory: {os.getcwd()}")
print("Python files in directory:", [f for f in os.listdir('.') if f.endswith('.py')])

# Check if weather_charts directory exists
print(f"\nChecking weather_charts directory...")
if os.path.exists('weather_charts'):
    print("OK: weather_charts directory exists")
    files = os.listdir('weather_charts')
    print(f"Files in weather_charts/: {files}")
else:
    print("ERROR: weather_charts directory not found!")
    sys.exit(1)

# Check key files
print("\nChecking key files...")
files_to_check = ['__init__.py', 'main.py', 'fetchers/openweather.py']
for file in files_to_check:
    path = os.path.join('weather_charts', file)
    if os.path.exists(path):
        size = os.path.getsize(path)
        print(f"OK: {file} exists ({size} bytes)")
    else:
        print(f"ERROR: {file} not found!")

# Test import
print("\nTesting import...")
try:
    # Add current directory to path
    sys.path.insert(0, os.getcwd())
    
    import weather_charts
    print("OK: Imported weather_charts package")
    
    # Check version
    if hasattr(weather_charts, '__version__'):
        print(f"OK: Version = {weather_charts.__version__}")
    else:
        print("WARNING: No __version__ attribute")
        
except ImportError as e:
    print(f"ERROR: Import failed: {e}")
    sys.exit(1)

# Try to import main class
print("\nTesting WeatherCharts class import...")
try:
    from weather_charts.main import WeatherCharts
    print("OK: Imported WeatherCharts class")
    
    # Try to create instance
    weather = WeatherCharts(api_key="dummy_key_for_test")
    print("OK: Created WeatherCharts instance")
    
    # Check methods
    methods = ['get_weather_graph', 'get_weather_data']
    for method in methods:
        if hasattr(weather, method):
            print(f"OK: Has {method}() method")
        else:
            print(f"WARNING: Missing {method}() method")
            
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}")

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)