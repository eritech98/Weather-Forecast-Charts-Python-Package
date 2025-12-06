"""
Plotly-based chart generator for interactive weather visualizations.
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
from typing import Dict, List, Optional, Any
import json
from datetime import datetime

class PlotlyGenerator:
    """Generates interactive charts using Plotly."""
    
    def __init__(self, 
                 width: int = 1000,
                 height: int = 600,
                 template: str = 'plotly_white'):
        """
        Initialize Plotly generator.
        
        Args:
            width: Chart width in pixels
            height: Chart height in pixels
            template: Plotly template name
        """
        self.width = width
        self.height = height
        self.template = template
        
        # Color scheme
        self.colors = {
            'temperature': '#FF6B6B',
            'humidity': '#4ECDC4',
            'rainfall': '#45B7D1',
            'wind': '#96CEB4',
            'pressure': '#FFEAA7',
            'feels_like': '#FFA726'
        }
    
    def generate_chart(self, 
                       weather_data: Dict,
                       graph_type: str = 'temperature',
                       title: Optional[str] = None) -> str:
        """
        Generate interactive Plotly chart.
        
        Args:
            weather_data: Weather data dictionary
            graph_type: Type of chart to generate
            title: Chart title
            
        Returns:
            HTML string containing the chart
        """
        forecast = weather_data['forecast']
        dates = [entry['datetime'] for entry in forecast]
        
        if graph_type == 'temperature':
            fig = self._create_temperature_chart(weather_data, dates, title)
        elif graph_type == 'humidity':
            fig = self._create_humidity_chart(weather_data, dates, title)
        elif graph_type == 'rainfall':
            fig = self._create_rainfall_chart(weather_data, dates, title)
        elif graph_type == 'wind':
            fig = self._create_wind_chart(weather_data, dates, title)
        elif graph_type == 'pressure':
            fig = self._create_pressure_chart(weather_data, dates, title)
        elif graph_type == 'composite':
            fig = self._create_composite_chart(weather_data, dates, title)
        else:
            raise ValueError(f"Unsupported graph type: {graph_type}")
        
        # Update layout
        fig.update_layout(
            width=self.width,
            height=self.height,
            template=self.template,
            hovermode='x unified',
            showlegend=True
        )
        
        return fig.to_html(include_plotlyjs=True, full_html=False)
    
    def _create_temperature_chart(self, weather_data: Dict, dates: List, title: str) -> go.Figure:
        """Create interactive temperature chart."""
        forecast = weather_data['forecast']
        
        fig = go.Figure()
        
        # Main temperature line
        fig.add_trace(go.Scatter(
            x=dates,
            y=[entry['temperature'] for entry in forecast],
            mode='lines+markers',
            name='Temperature',
            line=dict(color=self.colors['temperature'], width=3),
            marker=dict(size=6),
            hovertemplate='%{x|%a %H:%M}<br>Temp: %{y:.1f}°C<extra></extra>'
        ))
        
        # Feels like temperature
        fig.add_trace(go.Scatter(
            x=dates,
            y=[entry['feels_like'] for entry in forecast],
            mode='lines',
            name='Feels Like',
            line=dict(color=self.colors['feels_like'], width=2, dash='dash'),
            hovertemplate='%{x|%a %H:%M}<br>Feels Like: %{y:.1f}°C<extra></extra>'
        ))
        
        # Min/Max range
        fig.add_trace(go.Scatter(
            x=dates + dates[::-1],  # x, then x reversed
            y=[entry['temp_max'] for entry in forecast] + 
              [entry['temp_min'] for entry in forecast][::-1],
            fill='toself',
            fillcolor='rgba(255, 107, 107, 0.2)',
            line=dict(color='rgba(255,255,255,0)'),
            hoverinfo='skip',
            showlegend=True,
            name='Min/Max Range'
        ))
        
        location = weather_data['location']
        default_title = f"Temperature in {location['city']}, {location['country']}"
        
        fig.update_layout(
            title=title or default_title,
            xaxis_title="Date & Time",
            yaxis_title=f"Temperature ({weather_data['units']['temperature']})",
            xaxis=dict(
                tickformat='%a\n%H:%M',
                tickangle=0
            )
        )
        
        return fig
    
    def _create_humidity_chart(self, weather_data: Dict, dates: List, title: str) -> go.Figure:
        """Create interactive humidity chart."""
        forecast = weather_data['forecast']
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=dates,
            y=[entry['humidity'] for entry in forecast],
            name='Humidity',
            marker_color=self.colors['humidity'],
            hovertemplate='%{x|%a %H:%M}<br>Humidity: %{y}%<extra></extra>',
            opacity=0.7
        ))
        
        location = weather_data['location']
        default_title = f"Humidity in {location['city']}, {location['country']}"
        
        fig.update_layout(
            title=title or default_title,
            xaxis_title="Date & Time",
            yaxis_title="Humidity (%)",
            xaxis=dict(
                tickformat='%a\n%H:%M',
                tickangle=0
            ),
            yaxis=dict(range=[0, 105])
        )
        
        return fig
    
    def _create_rainfall_chart(self, weather_data: Dict, dates: List, title: str) -> go.Figure:
        """Create interactive rainfall chart."""
        forecast = weather_data['forecast']
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=dates,
            y=[entry['rainfall'] for entry in forecast],
            name='Rainfall',
            marker_color=self.colors['rainfall'],
            hovertemplate='%{x|%a %H:%M}<br>Rainfall: %{y:.1f}mm<extra></extra>',
            opacity=0.8
        ))
        
        location = weather_data['location']
        default_title = f"Rainfall in {location['city']}, {location['country']}"
        
        fig.update_layout(
            title=title or default_title,
            xaxis_title="Date & Time",
            yaxis_title=f"Rainfall ({weather_data['units']['rainfall']})",
            xaxis=dict(
                tickformat='%a\n%H:%M',
                tickangle=0
            )
        )
        
        return fig
    
    def _create_wind_chart(self, weather_data: Dict, dates: List, title: str) -> go.Figure:
        """Create interactive wind chart."""
        forecast = weather_data['forecast']
        
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        # Wind speed
        fig.add_trace(go.Scatter(
            x=dates,
            y=[entry['wind_speed'] for entry in forecast],
            mode='lines+markers',
            name='Wind Speed',
            line=dict(color=self.colors['wind'], width=3),
            marker=dict(size=6),
            hovertemplate='%{x|%a %H:%M}<br>Speed: %{y:.1f} m/s<extra></extra>'
        ), secondary_y=False)
        
        # Wind direction as arrows (simplified)
        fig.add_trace(go.Scatter(
            x=dates,
            y=[entry['wind_deg'] for entry in forecast],
            mode='markers',
            name='Wind Direction',
            marker=dict(
                size=10,
                color=[entry['wind_speed'] for entry in forecast],
                colorscale='Blues',
                showscale=True,
                colorbar=dict(title="Speed (m/s)")
            ),
            hovertemplate='%{x|%a %H:%M}<br>Direction: %{y}°<extra></extra>'
        ), secondary_y=True)
        
        location = weather_data['location']
        default_title = f"Wind in {location['city']}, {location['country']}"
        
        fig.update_layout(
            title=title or default_title,
            xaxis_title="Date & Time",
            xaxis=dict(
                tickformat='%a\n%H:%M',
                tickangle=0
            )
        )
        
        fig.update_yaxes(
            title_text=f"Wind Speed ({weather_data['units']['speed']})",
            secondary_y=False
        )
        fig.update_yaxes(
            title_text="Wind Direction (°)",
            range=[0, 360],
            secondary_y=True
        )
        
        return fig
    
    def _create_pressure_chart(self, weather_data: Dict, dates: List, title: str) -> go.Figure:
        """Create interactive pressure chart."""
        forecast = weather_data['forecast']
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=dates,
            y=[entry['pressure'] for entry in forecast],
            mode='lines+markers',
            name='Pressure',
            line=dict(color=self.colors['pressure'], width=3),
            marker=dict(size=6),
            fill='tozeroy',
            fillcolor='rgba(255, 234, 167, 0.3)',
            hovertemplate='%{x|%a %H:%M}<br>Pressure: %{y} hPa<extra></extra>'
        ))
        
        # Add average line
        avg_pressure = sum(entry['pressure'] for entry in forecast) / len(forecast)
        fig.add_hline(
            y=avg_pressure,
            line_dash="dash",
            line_color="red",
            annotation_text=f"Average: {avg_pressure:.1f} hPa",
            annotation_position="bottom right"
        )
        
        location = weather_data['location']
        default_title = f"Pressure in {location['city']}, {location['country']}"
        
        fig.update_layout(
            title=title or default_title,
            xaxis_title="Date & Time",
            yaxis_title=f"Pressure ({weather_data['units']['pressure']})",
            xaxis=dict(
                tickformat='%a\n%H:%M',
                tickangle=0
            )
        )
        
        return fig
    
    def _create_composite_chart(self, weather_data: Dict, dates: List, title: str) -> go.Figure:
        """Create composite chart with multiple variables."""
        forecast = weather_data['forecast']
        
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Temperature', 'Humidity', 'Rainfall', 'Wind Speed'),
            vertical_spacing=0.15,
            horizontal_spacing=0.15
        )
        
        # Temperature subplot
        fig.add_trace(go.Scatter(
            x=dates,
            y=[entry['temperature'] for entry in forecast],
            mode='lines',
            name='Temperature',
            line=dict(color=self.colors['temperature'], width=2)
        ), row=1, col=1)
        
        # Humidity subplot
        fig.add_trace(go.Bar(
            x=dates,
            y=[entry['humidity'] for entry in forecast],
            name='Humidity',
            marker_color=self.colors['humidity'],
            opacity=0.7
        ), row=1, col=2)
        
        # Rainfall subplot
        fig.add_trace(go.Bar(
            x=dates,
            y=[entry['rainfall'] for entry in forecast],
            name='Rainfall',
            marker_color=self.colors['rainfall'],
            opacity=0.7
        ), row=2, col=1)
        
        # Wind speed subplot
        fig.add_trace(go.Scatter(
            x=dates,
            y=[entry['wind_speed'] for entry in forecast],
            mode='lines',
            name='Wind Speed',
            line=dict(color=self.colors['wind'], width=2)
        ), row=2, col=2)
        
        location = weather_data['location']
        default_title = f"Weather Overview in {location['city']}, {location['country']}"
        
        fig.update_layout(
            title_text=title or default_title,
            showlegend=False,
            height=800
        )
        
        # Update x-axis for all subplots
        for i in [1, 2]:
            for j in [1, 2]:
                fig.update_xaxes(
                    tickformat='%a\n%H:%M',
                    row=i, col=j
                )
        
        # Update y-axis labels
        fig.update_yaxes(
            title_text=f"Temp ({weather_data['units']['temperature']})",
            row=1, col=1
        )
        fig.update_yaxes(
            title_text="Humidity (%)",
            row=1, col=2
        )
        fig.update_yaxes(
            title_text=f"Rainfall ({weather_data['units']['rainfall']})",
            row=2, col=1
        )
        fig.update_yaxes(
            title_text=f"Wind ({weather_data['units']['speed']})",
            row=2, col=2
        )
        
        return fig