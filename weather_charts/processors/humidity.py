"""
Humidity data processor.
"""

from typing import Dict, List, Any
import statistics

class HumidityProcessor:
    """Processes humidity data for chart generation."""
    
    def process(self, weather_data: Dict) -> Dict[str, Any]:
        """
        Process humidity data.
        
        Args:
            weather_data: Raw weather data
            
        Returns:
            Processed humidity data
        """
        forecast = weather_data['forecast']
        
        times = [entry['datetime'] for entry in forecast]
        humidities = [entry['humidity'] for entry in forecast]
        
        # Calculate statistics
        stats = {
            'mean': statistics.mean(humidities),
            'median': statistics.median(humidities),
            'min': min(humidities),
            'max': max(humidities),
            'range': max(humidities) - min(humidities)
        }
        
        # Categorize humidity levels
        categories = []
        for humidity in humidities:
            if humidity < 30:
                categories.append('dry')
            elif humidity < 60:
                categories.append('comfortable')
            elif humidity < 80:
                categories.append('humid')
            else:
                categories.append('very_humid')
        
        return {
            'times': times,
            'humidities': humidities,
            'stats': stats,
            'categories': categories,
            'unit': '%'
        }