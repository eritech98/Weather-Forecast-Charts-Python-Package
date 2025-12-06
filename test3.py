# test_final_verification.py
from weather_charts import WeatherCharts
from datetime import datetime
import matplotlib.pyplot as plt

print("FINAL VERIFICATION TEST")
print("=" * 60)

# Variables that can be changed
API_KEY = "your api key here"
LOCATION = "Bomet"
DAYS = 1
CHART_TYPES_CONFIG = [
    ("temperature", "temperature"),
    ("humidity", "humidity"),
    ("rainfall", "rainfall"),
    ("wind", "wind"),
    ("pressure", "pressure"),
]

# Initialize
weather = WeatherCharts(api_key=API_KEY)

# Get data
data = weather.get_weather_data(LOCATION, days=DAYS)

print("1. Data Verification:")
print(f"   Current system date: {datetime.now()}")
print(f"   First forecast date: {data['forecast'][0]['datetime']}")
print(f"   Last forecast date: {data['forecast'][-1]['datetime']}")

# Check date range
date_range = (data['forecast'][-1]['datetime'] - data['forecast'][0]['datetime']).days
print(f"   Forecast covers: {date_range} days")

print("\n2. Generating all chart types...")

# Generate all chart types
chart_types = []
for name, graph_type in CHART_TYPES_CONFIG:
    chart_types.append((name, weather.get_weather_graph, {"graph_type": graph_type, "days": DAYS}))

successful_charts = []
failed_charts = []

for name, method, kwargs in chart_types:
    try:
        print(f"\n   Creating {name} chart...")
        result = method(LOCATION, **kwargs)
        
        # Save the chart
        with open(f"_{name}_final.png", "wb") as f:
            f.write(result['chart'].getvalue())
        
        successful_charts.append(name)
        print(f"   Saved as 'image_{name}_final.png'")
        
        # Show metadata
        print(f"   Metadata: {result['metadata'].get('graph_type')} chart")
        print(f"   Generated at: {result['metadata'].get('generated_at')}")
        
    except Exception as e:
        failed_charts.append((name, str(e)))
        print(f"   Failed: {e}")

print("\n" + "=" * 60)
print("SUMMARY:")
print(f"Successful: {len(successful_charts)} charts")
print(f"Failed: {len(failed_charts)} charts")

if successful_charts:
    print(f"\nGenerated charts: {', '.join(successful_charts)}")
    print("Check the PNG files in your directory!")
    
if failed_charts:
    print(f"\nFailed charts:")
    for name, error in failed_charts:
        print(f"  {name}: {error}")

print("\n" + "=" * 60)
print("If dates appear as December 2025 in your charts,")
print("that's CORRECT because your system date IS December 2025.")