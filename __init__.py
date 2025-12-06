"""
Weather Charts - A Python package to fetch weather data and generate beautiful charts.
"""

from .main import WeatherCharts, get_weather_graph
from .fetchers import OpenWeatherFetcher, WeatherAPIFetcher
from .generators import MatplotlibGenerator, PlotlyGenerator

__version__ = "1.0.0"
__author__ = "Weather Charts Team"
__email__ = "support@weathercharts.com"

__all__ = [
    'WeatherCharts',
    'get_weather_graph',
    'OpenWeatherFetcher',
    'WeatherAPIFetcher',
    'MatplotlibGenerator',
    'PlotlyGenerator'
]