"""
Weather data fetchers for different APIs.
"""

from .openweather import OpenWeatherFetcher
# Remove weatherapi import since we don't have that file

__all__ = ['OpenWeatherFetcher']
