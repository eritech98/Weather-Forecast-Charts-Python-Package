"""
Rainfall data processor.
"""

from typing import Dict, List, Any
import statistics
from datetime import datetime, timedelta

class RainfallProcessor:
    """Processes rainfall data for chart generation."""
    
    def process(self, weather_data: Dict) -> Dict[str, Any]:
        """
        Process rainfall data.
        
        Args:
            weather_data: Raw weather data
            
        Returns:
            Processed rainfall data
        """
        forecast = weather_data['forecast']
        
        times = [entry['datetime'] for entry in forecast]
        rainfall = [entry['rainfall'] for entry in forecast]
        snowfall = [entry.get('snowfall', 0) for entry in forecast]
        
        # Calculate cumulative rainfall
        cumulative_rain = []
        cumulative_snow = []
        current_rain = 0
        current_snow = 0
        
        for rain, snow in zip(rainfall, snowfall):
            current_rain += rain
            current_snow += snow
            cumulative_rain.append(current_rain)
            cumulative_snow.append(current_snow)
        
        # Calculate statistics
        total_rainfall = sum(rainfall)
        total_snowfall = sum(snowfall)
        total_precipitation = total_rainfall + total_snowfall
        rainy_periods = sum(1 for rain in rainfall if rain > 0)
        snowy_periods = sum(1 for snow in snowfall if snow > 0)
        
        stats = {
            'total_rainfall': total_rainfall,
            'total_snowfall': total_snowfall,
            'total_precipitation': total_precipitation,
            'average_rainfall': statistics.mean(rainfall) if rainfall else 0,
            'max_rainfall': max(rainfall) if rainfall else 0,
            'max_snowfall': max(snowfall) if snowfall else 0,
            'rainy_periods': rainy_periods,
            'snowy_periods': snowy_periods,
            'rain_probability': rainy_periods / len(rainfall) * 100 if rainfall else 0,
            'snow_probability': snowy_periods / len(snowfall) * 100 if snowfall else 0
        }
        
        # Identify precipitation events
        rain_events = self._identify_precipitation_events(times, rainfall, 'rain')
        snow_events = self._identify_precipitation_events(times, snowfall, 'snow')
        
        # Categorize rainfall intensity
        intensity_categories = []
        for rain in rainfall:
            if rain == 0:
                intensity_categories.append('none')
            elif rain < 0.5:
                intensity_categories.append('light')
            elif rain < 4:
                intensity_categories.append('moderate')
            elif rain < 8:
                intensity_categories.append('heavy')
            else:
                intensity_categories.append('violent')
        
        # Calculate precipitation rates (mm/hour)
        rates = []
        for i in range(len(times)):
            if i == 0:
                rates.append(0)
            else:
                # Assuming 3-hour intervals in forecast
                hours_diff = 3
                rate = rainfall[i] / hours_diff
                rates.append(rate)
        
        return {
            'times': times,
            'rainfall': rainfall,
            'snowfall': snowfall,
            'cumulative_rain': cumulative_rain,
            'cumulative_snow': cumulative_snow,
            'rates': rates,
            'stats': stats,
            'rain_events': rain_events,
            'snow_events': snow_events,
            'intensity_categories': intensity_categories,
            'units': weather_data['units']['rainfall']
        }
    
    def _identify_precipitation_events(self, times: List[datetime], 
                                      precipitation: List[float], 
                                      precip_type: str) -> List[Dict]:
        """
        Identify distinct precipitation events.
        
        Args:
            times: List of timestamps
            precipitation: List of precipitation values
            precip_type: Type of precipitation ('rain' or 'snow')
            
        Returns:
            List of precipitation events
        """
        events = []
        current_event = None
        
        for time, precip in zip(times, precipitation):
            if precip > 0:
                if current_event is None:
                    current_event = {
                        'start': time,
                        'end': time,
                        'total': precip,
                        'peak': precip,
                        'duration': 1,
                        'type': precip_type,
                        'intensity': self._categorize_intensity(precip, precip_type)
                    }
                else:
                    current_event['end'] = time
                    current_event['total'] += precip
                    current_event['peak'] = max(current_event['peak'], precip)
                    current_event['duration'] += 1
                    # Update intensity if this period is more intense
                    current_intensity = self._categorize_intensity(precip, precip_type)
                    if self._intensity_level(current_intensity) > self._intensity_level(current_event['intensity']):
                        current_event['intensity'] = current_intensity
            else:
                if current_event is not None:
                    # Calculate average intensity
                    current_event['average'] = current_event['total'] / current_event['duration']
                    events.append(current_event)
                    current_event = None
        
        if current_event is not None:
            current_event['average'] = current_event['total'] / current_event['duration']
            events.append(current_event)
        
        return events
    
    def _categorize_intensity(self, amount: float, precip_type: str) -> str:
        """
        Categorize precipitation intensity.
        """
        if precip_type == 'rain':
            if amount == 0:
                return 'none'
            elif amount < 0.5:
                return 'light'
            elif amount < 4:
                return 'moderate'
            elif amount < 8:
                return 'heavy'
            else:
                return 'violent'
        else:  # snow
            if amount == 0:
                return 'none'
            elif amount < 0.5:
                return 'flurries'
            elif amount < 2:
                return 'light'
            elif amount < 5:
                return 'moderate'
            else:
                return 'heavy'
    
    def _intensity_level(self, intensity: str) -> int:
        """
        Convert intensity to numeric level for comparison.
        """
        levels = {
            'none': 0,
            'flurries': 1,
            'light': 2,
            'moderate': 3,
            'heavy': 4,
            'violent': 5
        }
        return levels.get(intensity, 0)
    
    def calculate_flood_risk(self, rainfall: List[float], 
                            cumulative_rain: List[float],
                            soil_saturation: float = 0.5) -> Dict[str, Any]:
        """
        Calculate flood risk based on rainfall patterns.
        
        Args:
            rainfall: List of rainfall amounts
            cumulative_rain: List of cumulative rainfall
            soil_saturation: Current soil saturation (0-1)
            
        Returns:
            Flood risk assessment
        """
        if not rainfall:
            return {'risk': 'low', 'score': 0, 'factors': []}
        
        risk_factors = []
        risk_score = 0
        
        # Factor 1: Total rainfall in last 24 hours
        recent_rain = sum(rainfall[-8:]) if len(rainfall) >= 8 else sum(rainfall)  # 8*3 = 24 hours
        if recent_rain > 50:
            risk_factors.append('heavy_24h_rainfall')
            risk_score += 3
        elif recent_rain > 25:
            risk_factors.append('moderate_24h_rainfall')
            risk_score += 2
        elif recent_rain > 10:
            risk_factors.append('light_24h_rainfall')
            risk_score += 1
        
        # Factor 2: Rainfall intensity
        max_hourly = max(rainfall) / 3  # Convert 3-hour to hourly
        if max_hourly > 20:
            risk_factors.append('extreme_intensity')
            risk_score += 3
        elif max_hourly > 10:
            risk_factors.append('high_intensity')
            risk_score += 2
        elif max_hourly > 5:
            risk_factors.append('moderate_intensity')
            risk_score += 1
        
        # Factor 3: Soil saturation
        if soil_saturation > 0.8:
            risk_factors.append('high_soil_saturation')
            risk_score += 2
        elif soil_saturation > 0.6:
            risk_factors.append('moderate_soil_saturation')
            risk_score += 1
        
        # Determine risk level
        if risk_score >= 5:
            risk_level = 'high'
        elif risk_score >= 3:
            risk_level = 'moderate'
        elif risk_score >= 1:
            risk_level = 'low'
        else:
            risk_level = 'very_low'
        
        return {
            'risk': risk_level,
            'score': risk_score,
            'factors': risk_factors,
            'recent_24h_rain': recent_rain,
            'max_hourly_intensity': max_hourly
        }