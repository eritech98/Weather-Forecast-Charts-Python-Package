"""
Main module for Weather Charts package.
"""

from typing import Union, Dict, Optional, Any, BinaryIO
from datetime import datetime
from .fetchers.openweather import OpenWeatherFetcher
from .generators.matplotlib_generator import MatplotlibGenerator
from .generators.plotly_generator import PlotlyGenerator

class WeatherCharts:
    """
    Main class for fetching weather data and generating charts.
    
    Example:
        >>> weather = WeatherCharts(api_key="your_api_key")
        >>> result = weather.get_weather_graph("Nairobi", graph_type="temperature")
        >>> with open("chart.png", "wb") as f:
        ...     f.write(result["chart"].read())
    """
    
    def __init__(self, api_key: str, options: Optional[Dict] = None):
        """
        Initialize WeatherCharts with API key and options.
        
        Args:
            api_key: OpenWeatherMap API key
            options: Optional configuration dictionary
        """
        self.api_key = api_key
        self.options = options or {}
        
        # Initialize fetcher
        self.fetcher = OpenWeatherFetcher(api_key)
        
        # Initialize generators based on options
        self.matplotlib_generator = MatplotlibGenerator(
            figsize=self.options.get('figsize', (10, 6)),
            style=self.options.get('style', 'seaborn-v0_8')
        )
        
        self.plotly_generator = PlotlyGenerator(
            width=self.options.get('width', 1000),
            height=self.options.get('height', 600),
            template=self.options.get('template', 'plotly_white')
        )
    
    def get_weather_data(self, 
                         location: Union[str, Dict], 
                         days: int = 5,
                         units: str = 'metric') -> Dict:
        """
        Fetch weather data for a location.
        
        Args:
            location: City name (str) or coordinates dict {'lat': float, 'lon': float}
            days: Number of forecast days (1-5)
            units: Temperature units ('metric', 'imperial', 'standard')
            
        Returns:
            Dictionary with weather data
        """
        days = max(1, min(days, 5))  # OpenWeather free tier limits to 5 days
        
        if isinstance(location, str):
            return self.fetcher.fetch_by_city(location, days=days, units=units)
        elif isinstance(location, dict) and 'lat' in location and 'lon' in location:
            return self.fetcher.fetch_by_coords(
                location['lat'], location['lon'], days=days, units=units
            )
        else:
            raise ValueError("Location must be string (city name) or dict with lat/lon keys")
    
    def get_weather_graph(self,
                          location: Union[str, Dict],
                          graph_type: str = 'temperature',
                          output_format: str = 'png',
                          **kwargs) -> Dict[str, Any]:
        """
        Get weather data and generate a chart.
        
        Args:
            location: City name or coordinates
            graph_type: Type of graph ('temperature', 'humidity', 'rainfall', 'wind', 'pressure')
            output_format: Output format ('png', 'html', 'json')
            **kwargs: Additional options passed to generators
            
        Returns:
            Dictionary containing weather data and chart
        """
        # Get weather data - only pass days and units to get_weather_data
        data_kwargs = {k: v for k, v in kwargs.items() if k in ['days', 'units']}
        weather_data = self.get_weather_data(location, **data_kwargs)
        
        # Separate kwargs for chart generation (remove days and units)
        chart_kwargs = {k: v for k, v in kwargs.items() if k not in ['days', 'units']}
        
        chart_buffer = None
        metadata = {
            'location': weather_data['location'],
            'graph_type': graph_type,
            'output_format': output_format,
            'generated_at': datetime.now().isoformat(),
            'units': kwargs.get('units', 'metric')
        }
        
        # Generate chart based on format
        if output_format in ['png', 'jpg', 'svg']:
            if graph_type == 'temperature':
                chart_buffer = self.matplotlib_generator.generate_temperature_chart(
                    weather_data, **chart_kwargs
                )
            elif graph_type == 'humidity':
                chart_buffer = self.matplotlib_generator.generate_humidity_chart(
                    weather_data, **chart_kwargs
                )
            elif graph_type == 'rainfall':
                chart_buffer = self.matplotlib_generator.generate_rainfall_chart(
                    weather_data, **chart_kwargs
                )
            elif graph_type == 'wind':
                chart_buffer = self.matplotlib_generator.generate_wind_chart(
                    weather_data, **chart_kwargs
                )
            elif graph_type == 'pressure':
                chart_buffer = self.matplotlib_generator.generate_pressure_chart(
                    weather_data, **chart_kwargs
                )
            elif graph_type == 'composite':
                chart_buffer = self.matplotlib_generator.generate_composite_chart(
                    weather_data, **chart_kwargs
                )
            else:
                raise ValueError(f"Unsupported graph type: {graph_type}")
        
        elif output_format == 'html':
            # Use Plotly for interactive HTML charts
            chart_buffer = self.plotly_generator.generate_chart(
                weather_data, graph_type=graph_type, **chart_kwargs
            )
        
        else:
            raise ValueError(f"Unsupported output format: {output_format}")
        
        return {
            'data': weather_data,
            'chart': chart_buffer,
            'metadata': metadata
        }
    
    def save_graph(self, chart_buffer: BinaryIO, filename: str) -> None:
        """
        Save chart buffer to file.
        
        Args:
            chart_buffer: Binary buffer containing chart
            filename: Output filename
        """
        with open(filename, 'wb') as f:
            if hasattr(chart_buffer, 'getvalue'):
                # For BytesIO objects
                f.write(chart_buffer.getvalue())
            elif hasattr(chart_buffer, 'read'):
                # For file-like objects
                chart_buffer.seek(0)
                f.write(chart_buffer.read())
            elif isinstance(chart_buffer, bytes):
                # For raw bytes
                f.write(chart_buffer)
            else:
                raise TypeError(f"Unsupported chart buffer type: {type(chart_buffer)}")


def get_weather_graph(location: Union[str, Dict], 
                      api_key: str,
                      graph_type: str = 'temperature',
                      **kwargs) -> Dict[str, Any]:
    """
    Convenience function to get weather graph in one call.
    
    Example:
        >>> result = get_weather_graph("Nairobi", api_key="abc123", graph_type="temperature")
        >>> result['chart']  # PNG buffer
    """
    weather = WeatherCharts(api_key)
    return weather.get_weather_graph(location, graph_type=graph_type, **kwargs)