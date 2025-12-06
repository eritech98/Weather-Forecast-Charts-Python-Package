#!/usr/bin/env python3
"""
Flask web server example for weather-charts package.
"""

import os
from flask import Flask, render_template_string, send_file, request, jsonify
from io import BytesIO
from weather_charts import WeatherCharts

app = Flask(__name__)

# Initialize weather charts
api_key = 'your_api_key'
if not api_key:
    raise ValueError("Please set OPENWEATHER_API_KEY environment variable")

weather = WeatherCharts(api_key)

# HTML template for the web interface
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Weather Charts Web Interface</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        header {
            background: linear-gradient(90deg, #4b6cb7 0%, #182848 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        h1 { 
            font-size: 2.5em; 
            margin-bottom: 10px; 
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        .subtitle { 
            font-size: 1.2em; 
            opacity: 0.9; 
        }
        .main-content {
            padding: 40px;
            display: grid;
            grid-template-columns: 1fr 2fr;
            gap: 40px;
        }
        .controls {
            background: #f8f9fa;
            padding: 25px;
            border-radius: 15px;
            box-shadow: inset 0 2px 10px rgba(0,0,0,0.05);
        }
        .form-group {
            margin-bottom: 25px;
        }
        label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: #333;
        }
        input, select {
            width: 100%;
            padding: 12px 15px;
            border: 2px solid #ddd;
            border-radius: 10px;
            font-size: 16px;
            transition: border-color 0.3s;
        }
        input:focus, select:focus {
            outline: none;
            border-color: #4b6cb7;
        }
        button {
            width: 100%;
            padding: 15px;
            background: linear-gradient(90deg, #4b6cb7 0%, #182848 100%);
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 18px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(75, 108, 183, 0.3);
        }
        .chart-container {
            background: white;
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            text-align: center;
        }
        .chart-img {
            max-width: 100%;
            height: auto;
            border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        .loading {
            display: none;
            text-align: center;
            padding: 20px;
            color: #666;
        }
        .error {
            color: #e74c3c;
            background: #ffeaea;
            padding: 15px;
            border-radius: 10px;
            margin-top: 20px;
            display: none;
        }
        .weather-info {
            margin-top: 20px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 10px;
            display: none;
        }
        footer {
            text-align: center;
            padding: 20px;
            color: #666;
            border-top: 1px solid #eee;
            background: #f8f9fa;
        }
        @media (max-width: 900px) {
            .main-content {
                grid-template-columns: 1fr;
            }
            h1 { font-size: 2em; }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🌤️ Weather Charts</h1>
            <p class="subtitle">Visualize weather data from anywhere in the world</p>
        </header>
        
        <div class="main-content">
            <div class="controls">
                <h2>Get Weather Chart</h2>
                <form id="weatherForm">
                    <div class="form-group">
                        <label for="location">Location:</label>
                        <input type="text" id="location" name="location" 
                               placeholder="Enter city name (e.g., Nairobi)" required
                               value="Nairobi">
                    </div>
                    
                    <div class="form-group">
                        <label for="graphType">Chart Type:</label>
                        <select id="graphType" name="graphType">
                            <option value="temperature">Temperature</option>
                            <option value="humidity">Humidity</option>
                            <option value="rainfall">Rainfall</option>
                            <option value="wind">Wind</option>
                            <option value="pressure">Pressure</option>
                            <option value="composite">Composite</option>
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label for="days">Forecast Days (1-5):</label>
                        <input type="number" id="days" name="days" 
                               min="1" max="5" value="3">
                    </div>
                    
                    <div class="form-group">
                        <label for="units">Units:</label>
                        <select id="units" name="units">
                            <option value="metric">Metric (°C, m/s)</option>
                            <option value="imperial">Imperial (°F, mph)</option>
                        </select>
                    </div>
                    
                    <button type="submit">Generate Chart</button>
                </form>
                
                <div class="loading" id="loading">
                    <p>⏳ Generating your weather chart...</p>
                </div>
                
                <div class="error" id="error"></div>
                
                <div class="weather-info" id="weatherInfo">
                    <h3>Weather Information</h3>
                    <p id="locationInfo"></p>
                    <p id="tempInfo"></p>
                    <p id="humidityInfo"></p>
                    <p id="windInfo"></p>
                </div>
            </div>
            
            <div class="chart-container">
                <h2>Weather Chart</h2>
                <div id="chartPlaceholder">
                    <p style="color: #666; padding: 50px;">
                        Enter location and click "Generate Chart" to see weather visualization
                    </p>
                </div>
                <img id="chartImage" class="chart-img" style="display: none;">
            </div>
        </div>
        
        <footer>
            <p>Powered by OpenWeatherMap API | Weather Charts Package v1.0</p>
        </footer>
    </div>
    
    <script>
        document.getElementById('weatherForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const params = new URLSearchParams(formData);
            
            // Show loading, hide previous results
            document.getElementById('loading').style.display = 'block';
            document.getElementById('error').style.display = 'none';
            document.getElementById('weatherInfo').style.display = 'none';
            document.getElementById('chartImage').style.display = 'none';
            
            try {
                // Get chart
                const chartResponse = await fetch(`/weather-chart?${params}`);
                if (!chartResponse.ok) {
                    throw new Error('Failed to generate chart');
                }
                
                // Get weather data
                const dataResponse = await fetch(`/weather-data?${params}`);
                if (!dataResponse.ok) {
                    throw new Error('Failed to get weather data');
                }
                
                const weatherData = await dataResponse.json();
                
                // Create image from blob
                const chartBlob = await chartResponse.blob();
                const chartUrl = URL.createObjectURL(chartBlob);
                
                // Display chart
                const chartImg = document.getElementById('chartImage');
                chartImg.src = chartUrl;
                chartImg.style.display = 'block';
                document.getElementById('chartPlaceholder').style.display = 'none';
                
                // Display weather info
                const forecast = weatherData.forecast[0];
                document.getElementById('locationInfo').textContent = 
                    `📍 ${weatherData.location.city}, ${weatherData.location.country}`;
                document.getElementById('tempInfo').textContent = 
                    `🌡️ Temperature: ${forecast.temperature}${weatherData.units.temperature} (Feels like: ${forecast.feels_like}${weatherData.units.temperature})`;
                document.getElementById('humidityInfo').textContent = 
                    `💧 Humidity: ${forecast.humidity}%`;
                document.getElementById('windInfo').textContent = 
                    `💨 Wind: ${forecast.wind_speed} ${weatherData.units.speed} at ${forecast.wind_deg}°`;
                
                document.getElementById('weatherInfo').style.display = 'block';
                
            } catch (error) {
                document.getElementById('error').textContent = `Error: ${error.message}`;
                document.getElementById('error').style.display = 'block';
            } finally {
                document.getElementById('loading').style.display = 'none';
            }
        });
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    """Render the main page."""
    return render_template_string(HTML_TEMPLATE)

@app.route('/weather-chart')
def get_chart():
    """Generate and return weather chart as PNG."""
    try:
        location = request.args.get('location', 'Nairobi')
        graph_type = request.args.get('graphType', 'temperature')
        days = int(request.args.get('days', 3))
        units = request.args.get('units', 'metric')
        
        # Generate chart
        result = weather.get_weather_graph(
            location=location,
            graph_type=graph_type,
            days=days,
            units=units,
            output_format='png'
        )
        
        # Return PNG image
        return send_file(
            BytesIO(result['chart'].read()),
            mimetype='image/png',
            as_attachment=False,
            download_name=f'weather_chart_{location}_{graph_type}.png'
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/weather-data')
def get_weather_data():
    """Return weather data as JSON."""
    try:
        location = request.args.get('location', 'Nairobi')
        days = int(request.args.get('days', 3))
        units = request.args.get('units', 'metric')
        
        # Get weather data
        data = weather.get_weather_data(
            location=location,
            days=days,
            units=units
        )
        
        return jsonify(data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/weather')
def api_weather():
    """API endpoint for weather data."""
    location = request.args.get('location')
    if not location:
        return jsonify({'error': 'Location parameter required'}), 400
    
    try:
        data = weather.get_weather_data(location)
        return jsonify({
            'success': True,
            'data': data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    print("Starting Weather Charts web server...")
    print("Open http://localhost:5000 in your browser")
    app.run(debug=True, host='0.0.0.0', port=5000)