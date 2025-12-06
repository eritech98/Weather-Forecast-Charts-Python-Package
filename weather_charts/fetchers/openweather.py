"""
OpenWeatherMap API fetcher.
"""

import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import time
from .base_fetcher import BaseWeatherFetcher

class OpenWeatherFetcher(BaseWeatherFetcher):
    """Fetches weather data from OpenWeatherMap API."""
    
    def __init__(self, api_key: str):
        """
        Initialize OpenWeatherMap fetcher.
        
        Args:
            api_key: OpenWeatherMap API key
        """
        self._validate_api_key(api_key)
        self.api_key = api_key
        self.base_url = "https://api.openweathermap.org/data/2.5"
        self.session = requests.Session()
    
    def fetch_by_city(self, 
                      city: str, 
                      days: int = 5,
                      units: str = 'metric',
                      lang: str = 'en') -> Dict:
        """
        Fetch weather forecast by city name.
        
        Args:
            city: City name (e.g., "Nairobi")
            days: Number of forecast days (1-5 for free tier)
            units: Temperature units ('metric', 'imperial', 'standard')
            lang: Language code
            
        Returns:
            Normalized weather data dictionary
        """
        days = max(1, min(days, 5))  # Free tier limit
        cnt = days * 8  # 8 forecasts per day (3-hour intervals)
        
        url = f"{self.base_url}/forecast"
        params = {
            'q': city,
            'appid': self.api_key,
            'units': units,
            'cnt': cnt,
            'lang': lang
        }
        
        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            return self._normalize_data(response.json(), units)
            
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Failed to fetch weather data: {str(e)}")
    
    def fetch_by_coords(self, 
                        lat: float, 
                        lon: float, 
                        days: int = 5,
                        units: str = 'metric',
                        lang: str = 'en') -> Dict:
        """
        Fetch weather forecast by coordinates.
        
        Args:
            lat: Latitude
            lon: Longitude
            days: Number of forecast days (1-5)
            units: Temperature units
            lang: Language code
            
        Returns:
            Normalized weather data dictionary
        """
        days = max(1, min(days, 5))
        cnt = days * 8
        
        url = f"{self.base_url}/forecast"
        params = {
            'lat': lat,
            'lon': lon,
            'appid': self.api_key,
            'units': units,
            'cnt': cnt,
            'lang': lang
        }
        
        response = self.session.get(url, params=params, timeout=10)
        response.raise_for_status()
        return self._normalize_data(response.json(), units)
    
    def fetch_by_zip(self, 
                     zip_code: str, 
                     country: str = 'US',
                     days: int = 5,
                     units: str = 'metric') -> Dict:
        """
        Fetch weather forecast by zip code.
        
        Args:
            zip_code: Zip/postal code
            country: Country code
            days: Number of forecast days
            units: Temperature units
            
        Returns:
            Normalized weather data dictionary
        """
        days = max(1, min(days, 5))
        cnt = days * 8
        
        url = f"{self.base_url}/forecast"
        params = {
            'zip': f"{zip_code},{country}",
            'appid': self.api_key,
            'units': units,
            'cnt': cnt
        }
        
        response = self.session.get(url, params=params, timeout=10)
        response.raise_for_status()
        return self._normalize_data(response.json(), units)
    
    def fetch_current(self, city: str, units: str = 'metric') -> Dict:
        """
        Fetch current weather data.
        
        Args:
            city: City name
            units: Temperature units
            
        Returns:
            Current weather data
        """
        url = f"{self.base_url}/weather"
        params = {
            'q': city,
            'appid': self.api_key,
            'units': units
        }
        
        response = self.session.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        return {
            'location': {
                'city': data['name'],
                'country': data['sys']['country'],
                'coordinates': {
                    'lat': data['coord']['lat'],
                    'lon': data['coord']['lon']
                }
            },
            'current': {
                'timestamp': data['dt'] * 1000,
                'temperature': data['main']['temp'],
                'feels_like': data['main']['feels_like'],
                'temp_min': data['main']['temp_min'],
                'temp_max': data['main']['temp_max'],
                'pressure': data['main']['pressure'],
                'humidity': data['main']['humidity'],
                'wind_speed': data['wind']['speed'],
                'wind_deg': data['wind']['deg'],
                'clouds': data['clouds']['all'],
                'description': data['weather'][0]['description'],
                'icon': data['weather'][0]['icon'],
                'sunrise': datetime.fromtimestamp(data['sys']['sunrise']),
                'sunset': datetime.fromtimestamp(data['sys']['sunset'])
            }
        }
    
    def _normalize_data(self, api_data: Dict, units: str = 'metric') -> Dict:
        """
        Normalize OpenWeatherMap API response to standard format.
        
        Args:
            api_data: Raw API response
            units: Temperature units used
            
        Returns:
            Normalized weather data
        """
        temp_unit = '°C' if units == 'metric' else '°F' if units == 'imperial' else 'K'
        speed_unit = 'm/s' if units == 'metric' else 'mph'
        
        return {
            'source': 'openweathermap',
            'location': {
                'city': api_data['city']['name'],
                'country': api_data['city']['country'],
                'coordinates': {
                    'lat': api_data['city']['coord']['lat'],
                    'lon': api_data['city']['coord']['lon']
                },
                'timezone': api_data['city'].get('timezone', 0)
            },
            'units': {
                'temperature': temp_unit,
                'speed': speed_unit,
                'pressure': 'hPa',
                'rainfall': 'mm'
            },
            'forecast': [
                {
                    'timestamp': entry['dt'] * 1000,
                    'datetime': datetime.fromtimestamp(entry['dt']),
                    'temperature': entry['main']['temp'],
                    'feels_like': entry['main']['feels_like'],
                    'temp_min': entry['main']['temp_min'],
                    'temp_max': entry['main']['temp_max'],
                    'pressure': entry['main']['pressure'],
                    'sea_level': entry['main'].get('sea_level'),
                    'grnd_level': entry['main'].get('grnd_level'),
                    'humidity': entry['main']['humidity'],
                    'wind_speed': entry['wind']['speed'],
                    'wind_deg': entry['wind']['deg'],
                    'wind_gust': entry['wind'].get('gust', 0),
                    'rainfall': entry.get('rain', {}).get('3h', 0),
                    'snowfall': entry.get('snow', {}).get('3h', 0),
                    'clouds': entry['clouds']['all'],
                    'description': entry['weather'][0]['description'],
                    'icon': entry['weather'][0]['icon'],
                    'pop': entry.get('pop', 0),  # Probability of precipitation
                    'visibility': entry.get('visibility', 10000)
                }
                for entry in api_data['list']
            ],
            'metadata': {
                'fetched_at': datetime.now().isoformat(),
                'forecast_count': len(api_data['list']),
                'forecast_interval_hours': 3
            }
        }