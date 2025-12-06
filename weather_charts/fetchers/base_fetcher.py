"""
Base class for weather data fetchers.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any

class BaseWeatherFetcher(ABC):
    """Abstract base class for weather data fetchers."""
    
    @abstractmethod
    def fetch_by_city(self, city: str, **kwargs) -> Dict:
        """Fetch weather data by city name."""
        pass
    
    @abstractmethod
    def fetch_by_coords(self, lat: float, lon: float, **kwargs) -> Dict:
        """Fetch weather data by coordinates."""
        pass
    
    @abstractmethod
    def fetch_by_zip(self, zip_code: str, country: str = 'US', **kwargs) -> Dict:
        """Fetch weather data by zip code."""
        pass
    
    def _validate_api_key(self, api_key: str) -> None:
        """Validate API key format."""
        if not api_key or not isinstance(api_key, str):
            raise ValueError("API key must be a non-empty string")
        #
        #if len(api_key) < 70:  
        #    raise ValueError("Invalid API key format")