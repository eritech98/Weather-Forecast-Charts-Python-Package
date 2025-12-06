"""
Wind data processor.
"""

from typing import Dict, List, Any
import statistics
import math

class WindProcessor:
    """Processes wind data for chart generation."""
    
    def process(self, weather_data: Dict) -> Dict[str, Any]:
        """
        Process wind data.
        
        Args:
            weather_data: Raw weather data
            
        Returns:
            Processed wind data
        """
        forecast = weather_data['forecast']
        
        times = [entry['datetime'] for entry in forecast]
        speeds = [entry['wind_speed'] for entry in forecast]
        directions = [entry['wind_deg'] for entry in forecast]
        
        # Calculate statistics
        stats = {
            'mean_speed': statistics.mean(speeds),
            'max_speed': max(speeds),
            'min_speed': min(speeds),
            'gust_peak': max(entry.get('wind_gust', 0) for entry in forecast)
        }
        
        # Categorize wind speeds (Beaufort scale simplified)
        categories = []
        for speed in speeds:
            if speed < 0.5:
                categories.append('calm')
            elif speed < 1.5:
                categories.append('light')
            elif speed < 3.3:
                categories.append('gentle')
            elif speed < 5.5:
                categories.append('moderate')
            elif speed < 7.9:
                categories.append('fresh')
            elif speed < 10.7:
                categories.append('strong')
            else:
                categories.append('gale')
        
        # Analyze wind direction
        direction_stats = self._analyze_directions(directions)
        
        # Calculate wind components for vector display
        u_components = []  # East-West
        v_components = []  # North-South
        
        for speed, direction in zip(speeds, directions):
            # Convert direction to radians (0° = North, clockwise)
            rad = math.radians(270 - direction)  # Adjust for meteorological convention
            
            u = speed * math.cos(rad)  # Eastward component
            v = speed * math.sin(rad)  # Northward component
            
            u_components.append(u)
            v_components.append(v)
        
        return {
            'times': times,
            'speeds': speeds,
            'directions': directions,
            'u_components': u_components,
            'v_components': v_components,
            'stats': stats,
            'categories': categories,
            'direction_stats': direction_stats,
            'unit': weather_data['units']['speed']
        }
    
    def _analyze_directions(self, directions: List[float]) -> Dict[str, Any]:
        """
        Analyze wind direction patterns.
        
        Args:
            directions: List of wind directions in degrees
            
        Returns:
            Direction analysis
        """
        if not directions:
            return {}
        
        # Categorize directions
        direction_categories = {'N': 0, 'NE': 0, 'E': 0, 'SE': 0, 
                               'S': 0, 'SW': 0, 'W': 0, 'NW': 0}
        
        for direction in directions:
            # Convert to cardinal direction
            index = int((direction + 22.5) / 45) % 8
            cardinals = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
            direction_categories[cardinals[index]] += 1
        
        # Find prevailing direction
        prevailing = max(direction_categories.items(), key=lambda x: x[1])
        
        return {
            'categories': direction_categories,
            'prevailing': prevailing[0],
            'prevailing_count': prevailing[1],
            'total_samples': len(directions)
        }