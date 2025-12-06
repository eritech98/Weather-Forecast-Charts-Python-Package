"""
Temperature data processor.
"""

from typing import Dict, List, Any
import statistics

class TemperatureProcessor:
    """Processes temperature data for chart generation."""
    
    def process(self, weather_data: Dict) -> Dict[str, Any]:
        """
        Process temperature data.
        
        Args:
            weather_data: Raw weather data
            
        Returns:
            Processed temperature data
        """
        forecast = weather_data['forecast']
        
        # Extract time series data
        times = [entry['datetime'] for entry in forecast]
        temperatures = [entry['temperature'] for entry in forecast]
        feels_like = [entry['feels_like'] for entry in forecast]
        temp_min = [entry['temp_min'] for entry in forecast]
        temp_max = [entry['temp_max'] for entry in forecast]
        
        # Calculate statistics
        stats = {
            'mean': statistics.mean(temperatures),
            'median': statistics.median(temperatures),
            'min': min(temperatures),
            'max': max(temperatures),
            'range': max(temperatures) - min(temperatures),
            'feels_like_mean': statistics.mean(feels_like)
        }
        
        # Detect temperature trends
        trends = self._detect_trends(temperatures)
        
        return {
            'times': times,
            'temperatures': temperatures,
            'feels_like': feels_like,
            'temp_min': temp_min,
            'temp_max': temp_max,
            'stats': stats,
            'trends': trends,
            'units': weather_data['units']['temperature']
        }
    
    def _detect_trends(self, temperatures: List[float]) -> Dict[str, Any]:
        """
        Detect temperature trends.
        
        Args:
            temperatures: List of temperature values
            
        Returns:
            Trend analysis
        """
        if len(temperatures) < 2:
            return {'direction': 'stable', 'magnitude': 0}
        
        # Simple linear regression for trend
        x = list(range(len(temperatures)))
        n = len(x)
        
        sum_x = sum(x)
        sum_y = sum(temperatures)
        sum_xy = sum(x[i] * temperatures[i] for i in range(n))
        sum_x2 = sum(x_i * x_i for x_i in x)
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
        
        # Determine trend direction
        if slope > 0.1:
            direction = 'rising'
        elif slope < -0.1:
            direction = 'falling'
        else:
            direction = 'stable'
        
        return {
            'direction': direction,
            'slope': slope,
            'magnitude': abs(slope * n)
        }