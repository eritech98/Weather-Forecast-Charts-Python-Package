import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.figure import Figure
from matplotlib.axes import Axes
from matplotlib.patches import Rectangle
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, BinaryIO, Any
from io import BytesIO
from scipy.interpolate import make_interp_spline
class MatplotlibGenerator:
    """Generates responsive and visually enhanced static charts for weather data using Matplotlib."""
    def __init__(self, figsize: Tuple[int, int] = (14, 9), style: str = 'seaborn-v0_8-darkgrid', scale: float = 1.0):
        """
        Initialize the responsive Matplotlib generator.
        Args:
            figsize: Base figure size (width, height) in inches.
            style: Matplotlib style to use.
            scale: Scaling factor for all visual elements (default: 1.0).
        """
        self.base_figsize = figsize
        self.figsize = (figsize[0] * scale, figsize[1] * scale)
        self.scale = scale
        plt.style.use(style)
        # High-contrast, responsive color palette
        self.colors = {
            'temperature': ['#FF0000', '#FF8C00', '#FFD700'],  # Red to Gold gradient
            'humidity': ['#0066CC', '#0099FF', '#33CCCC'],     # Blue to Teal gradient
            'rainfall': ['#001A33', '#0066CC', '#66CCFF'],     # Dark to Light Blue
            'wind': ['#2E8B57', '#3CB371', '#90EE90'],         # Green gradient
            'pressure': ['#800080', '#9932CC', '#BA55D3'],     # Purple gradient
            'feels_like': '#FF6B35',
            'background': '#F8F9FA',
            'grid': '#E9ECEF',
            'text': '#212529',
            'highlight': '#FF6B6B',
            'success': '#28A745',
            'warning': '#FFC107',
            'danger': '#DC3545'
        }
        # Responsive chart configuration
        self.chart_config = {
            'title_fontsize': int(18 * scale),
            'label_fontsize': int(12 * scale),
            'tick_fontsize': int(10 * scale),
            'legend_fontsize': int(10 * scale),
            'grid_alpha': 0.3 * min(scale, 1.0),
            'line_width': 2.5 * scale,
            'marker_size': int(8 * scale),
            'bar_width': 0.6 * scale,
            'dpi': 150 if scale >= 1.0 else 100
        }
    def generate_temperature_chart(
        self,
        weather_data: Dict,
        title: Optional[str] = None,
        show_feels_like: bool = True,
        show_min_max: bool = True,
        show_gradient: bool = True,
        simplify: bool = False
    ) -> BytesIO:
        """
        Generate a responsive temperature chart with gradient background.
        Args:
            weather_data: Weather data dictionary.
            title: Chart title (optional).
            show_feels_like: Show feels-like temperature.
            show_min_max: Show min/max temperature range.
            show_gradient: Show temperature gradient background.
            simplify: Simplify chart for small screens.
        Returns:
            Bytes buffer containing PNG image.
        """
        fig, ax = plt.subplots(figsize=self.figsize)
        forecast = weather_data['forecast']
        dates = [entry['datetime'] for entry in forecast]
        temps = [entry['temperature'] for entry in forecast]
        # Gradient background
        if show_gradient:
            temp_min, temp_max = min(temps), max(temps)
            for i in range(len(dates)-1):
                x1, x2 = dates[i], dates[i+1]
                y1, y2 = temps[i], temps[i+1]
                avg_temp = (y1 + y2) / 2
                temp_norm = (avg_temp - temp_min) / (temp_max - temp_min) if temp_max > temp_min else 0.5
                color_idx = int(temp_norm * (len(self.colors['temperature']) - 1))
                color = self.colors['temperature'][color_idx]
                x1_num = mdates.date2num(x1)
                x2_num = mdates.date2num(x2)
                rect = Rectangle(
                    (x1_num, 0),
                    x2_num - x1_num,
                    max(temps) + 5,
                    facecolor=color,
                    alpha=0.1,
                    edgecolor='none',
                    transform=ax.get_xaxis_transform()
                )
                ax.add_patch(rect)
        # Main temperature line
        line = ax.plot(
            dates, temps,
            linewidth=self.chart_config['line_width'] if not simplify else 1.5 * self.scale,
            marker='o' if not simplify else '',
            markersize=self.chart_config['marker_size'] if not simplify else 0,
            markerfacecolor=self.colors['highlight'],
            markeredgecolor='white',
            markeredgewidth=2 if not simplify else 0,
            zorder=5
        )[0]
        # Smooth curve
        if len(dates) > 3 and not simplify:
            try:
                date_nums = mdates.date2num(dates)
                x_smooth = np.linspace(date_nums.min(), date_nums.max(), 300)
                spline = make_interp_spline(date_nums, temps, k=3)
                y_smooth = spline(x_smooth)
                ax.plot(
                    mdates.num2date(x_smooth), y_smooth,
                    color=self.colors['temperature'][1],
                    alpha=0.3,
                    linewidth=4 * self.scale,
                    zorder=4
                )
            except Exception as e:
                pass
        # Feels-like temperature
        if show_feels_like and not simplify:
            feels_like = [entry['feels_like'] for entry in forecast]
            ax.plot(
                dates, feels_like,
                color=self.colors['feels_like'],
                linewidth=self.chart_config['line_width'] - 1,
                linestyle='--',
                alpha=0.8,
                marker='^' if not simplify else '',
                markersize=self.chart_config['marker_size'] - 2 if not simplify else 0,
                label='Feels Like',
                zorder=6
            )
        # Min/Max range
        if show_min_max and not simplify:
            temp_min = [entry['temp_min'] for entry in forecast]
            temp_max = [entry['temp_max'] for entry in forecast]
            ax.fill_between(
                dates, temp_min, temp_max,
                color=self.colors['temperature'][1],
                alpha=0.2,
                label='Temperature Range',
                zorder=3
            )
        # Temperature annotations
        if not simplify:
            for i, (date, temp) in enumerate(zip(dates, temps)):
                if i % (2 if len(dates) > 20 else 1) == 0:
                    ax.annotate(
                        f'{temp:.1f}°',
                        xy=(date, temp),
                        xytext=(0, 10),
                        textcoords='offset points',
                        ha='center',
                        fontsize=9 * self.scale,
                        color=self.colors['text'],
                        bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8, edgecolor='none')
                    )
        # Formatting
        self._format_responsive_chart(ax, weather_data, 'temperature', title)
        # Summary text
        avg_temp = np.mean(temps)
        max_temp = max(temps)
        min_temp = min(temps)
        summary_text = f"Avg: {avg_temp:.1f}°C | Max: {max_temp:.1f}°C | Min: {min_temp:.1f}°C"
        ax.text(
            0.02, 0.02, summary_text,
            transform=ax.transAxes,
            fontsize=10 * self.scale,
            bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.9, edgecolor=self.colors['grid'])
        )
        plt.tight_layout()
        return self._save_responsive_figure(fig)
    def generate_humidity_chart(
        self,
        weather_data: Dict,
        title: Optional[str] = None,
        show_comfort_zones: bool = True,
        simplify: bool = False
    ) -> BytesIO:
        """
        Generate a responsive humidity chart with comfort zones.
        Args:
            weather_data: Weather data dictionary.
            title: Chart title (optional).
            show_comfort_zones: Highlight comfort zones.
            simplify: Simplify chart for small screens.
        Returns:
            Bytes buffer containing PNG image.
        """
        fig, ax = plt.subplots(figsize=self.figsize)
        forecast = weather_data['forecast']
        dates = [entry['datetime'] for entry in forecast]
        humidity = [entry['humidity'] for entry in forecast]
        # Comfort zones
        if show_comfort_zones:
            ax.axhspan(40, 60, alpha=0.2, color=self.colors['success'], label='Comfort Zone (40-60%)', zorder=1)
            ax.axhspan(60, 100, alpha=0.15, color=self.colors['warning'], label='High Humidity', zorder=1)
            ax.axhspan(0, 40, alpha=0.15, color='#FFD700', label='Low Humidity', zorder=1)
        # Calculate the time interval between dates (in days)
        date_interval = (dates[-1] - dates[0]).total_seconds() / (86400 * (len(dates) - 1))
        # Set bar width to 40% of the interval
        bar_width = 0.4 * date_interval
        # Humidity bars
        bars = ax.bar(
            dates, humidity,
            color=[self._get_humidity_color(h) for h in humidity],
            alpha=0.85,
            width=bar_width,
            edgecolor='white',
            linewidth=1.5 * self.scale,
            zorder=5
        )
        # Value labels
        if not simplify:
            for bar, h in zip(bars, humidity):
                height = bar.get_height()
                color = 'black' if 40 <= height <= 60 else self.colors['text']
                ax.text(
                    bar.get_x() + bar.get_width()/2., height + 1,
                    f'{int(height)}%',
                    ha='center', va='bottom',
                    fontsize=9 * self.scale,
                    fontweight='bold' if height < 40 or height > 60 else 'normal',
                    color=color,
                    zorder=6
                )
        # Trend line
        if len(humidity) > 1 and not simplify:
            ax.plot(
                dates, humidity,
                color=self.colors['humidity'][1],
                linewidth=2 * self.scale,
                alpha=0.7,
                marker='',
                zorder=4
            )
        # Formatting
        self._format_responsive_chart(ax, weather_data, 'humidity', title)
        ax.set_ylim(0, 105)
        # Humidity statistics
        avg_humidity = np.mean(humidity)
        humidity_text = f"Average Humidity: {avg_humidity:.1f}%"
        if avg_humidity < 40:
            humidity_text += " (Low)"
        elif avg_humidity > 60:
            humidity_text += " (High)"
        else:
            humidity_text += " (Comfortable)"
        ax.text(
            0.02, 0.95, humidity_text,
            transform=ax.transAxes,
            fontsize=11 * self.scale,
            fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.9, edgecolor=self.colors['grid'])
        )
        plt.tight_layout()
        return self._save_responsive_figure(fig)
    def generate_rainfall_chart(
        self,
        weather_data: Dict,
        title: Optional[str] = None,
        cumulative: bool = False,
        show_intensity: bool = True,
        simplify: bool = False
    ) -> BytesIO:
        """
        Generate a responsive rainfall chart with intensity visualization.
        Args:
            weather_data: Weather data dictionary.
            title: Chart title (optional).
            cumulative: Show cumulative rainfall.
            show_intensity: Show rainfall intensity.
            simplify: Simplify chart for small screens.
        Returns:
            Bytes buffer containing PNG image.
        """
        fig, ax = plt.subplots(figsize=self.figsize)
        forecast = weather_data['forecast']
        dates = [entry['datetime'] for entry in forecast]
        rainfall = [entry['rainfall'] for entry in forecast]
        if cumulative:
            cumulative_rain = np.cumsum(rainfall)
            ax.fill_between(
                dates, 0, cumulative_rain,
                color=self.colors['rainfall'][0],
                alpha=0.4,
                label='Cumulative Rainfall',
                zorder=3
            )
            line = ax.plot(
                dates, cumulative_rain,
                color=self.colors['rainfall'][1],
                linewidth=3 * self.scale,
                marker='o' if not simplify else '',
                markersize=self.chart_config['marker_size'] if not simplify else 0,
                markerfacecolor='white',
                markeredgecolor=self.colors['rainfall'][1],
                markeredgewidth=2 if not simplify else 0,
                zorder=4
            )
            if cumulative_rain[-1] > 0:
                ax.annotate(
                    f'Total: {cumulative_rain[-1]:.1f}mm',
                    xy=(dates[-1], cumulative_rain[-1]),
                    xytext=(10, 0),
                    textcoords='offset points',
                    ha='left',
                    fontsize=10 * self.scale,
                    fontweight='bold',
                    bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.9)
                )
            ylabel = f"Cumulative Rainfall ({weather_data['units']['rainfall']})"
        else:
            # Calculate the time interval between dates (in days)
            date_interval = (dates[-1] - dates[0]).total_seconds() / (86400 * (len(dates) - 1))
            # Set bar width to 40% of the interval
            bar_width = 0.4 * date_interval
            bars = ax.bar(
                dates, rainfall,
                color=[self._get_rainfall_color(r) for r in rainfall],
                alpha=0.8,
                width=bar_width,
                edgecolor='white',
                linewidth=1.5 * self.scale,
                zorder=4
            )
            if not simplify:
                for bar, rain in zip(bars, rainfall):
                    if rain > 0.1:
                        height = bar.get_height()
                        ax.text(
                            bar.get_x() + bar.get_width()/2., height + 0.05,
                            f'{rain:.1f}',
                            ha='center', va='bottom',
                            fontsize=9 * self.scale,
                            fontweight='bold' if rain > 5 else 'normal',
                            color=self.colors['text']
                        )
            if show_intensity and not simplify:
                max_rain = max(rainfall) if rainfall else 0
                if max_rain > 0:
                    for i, rain in enumerate(rainfall):
                        if rain > 0:
                            intensity = min(rain / max_rain, 1)
                            ax.axvspan(
                                dates[i] - timedelta(hours=1.5),
                                dates[i] + timedelta(hours=1.5),
                                alpha=intensity * 0.1,
                                color=self.colors['rainfall'][0],
                                zorder=1
                            )
            ylabel = f"Rainfall ({weather_data['units']['rainfall']})"
        # Formatting
        self._format_responsive_chart(ax, weather_data, 'rainfall', title)
        ax.set_ylabel(ylabel, fontsize=self.chart_config['label_fontsize'], color=self.colors['text'], fontweight='bold')
        # Rainfall statistics
        total_rain = sum(rainfall)
        rainy_hours = sum(1 for r in rainfall if r > 0)
        max_rain = max(rainfall) if rainfall else 0
        stats_text = f"Total: {total_rain:.1f}mm | Max: {max_rain:.1f}mm | Rainy hours: {rainy_hours}"
        ax.text(
            0.02, 0.95, stats_text,
            transform=ax.transAxes,
            fontsize=10 * self.scale,
            bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.9, edgecolor=self.colors['grid'])
        )
        plt.tight_layout()
        return self._save_responsive_figure(fig)
    def generate_wind_chart(
        self,
        weather_data: Dict,
        title: Optional[str] = None,
        show_direction: bool = True,
        show_beaufort: bool = True,
        simplify: bool = False
    ) -> BytesIO:
        """
        Generate a responsive wind chart with Beaufort scale and direction visualization.
        Args:
            weather_data: Weather data dictionary.
            title: Chart title (optional).
            show_direction: Show wind direction.
            show_beaufort: Show Beaufort scale colors.
            simplify: Simplify chart for small screens.
        Returns:
            Bytes buffer containing PNG image.
        """
        fig, ax = plt.subplots(figsize=self.figsize)
        forecast = weather_data['forecast']
        dates = [entry['datetime'] for entry in forecast]
        wind_speed = [entry['wind_speed'] for entry in forecast]
        wind_deg = [entry['wind_deg'] for entry in forecast]
        # Beaufort scale
        beaufort_colors = {
            0: '#E8F4F8',  # Calm
            1: '#D4EDF7',  # Light air
            2: '#A8D5E2',  # Light breeze
            3: '#7CB8CC',  # Gentle breeze
            4: '#4F9BB5',  # Moderate breeze
            5: '#327E9E',  # Fresh breeze
            6: '#1A6187',  # Strong breeze
            7: '#0C4470'   # Near gale and above
        }
        if show_beaufort:
            beaufort_breaks = [0.5, 1.5, 3.3, 5.5, 7.9, 10.7, 13.8, 17.1]
            for i, (start, end) in enumerate(zip([0] + beaufort_breaks, beaufort_breaks + [100])):
                ax.axhspan(start, end, alpha=0.2, color=beaufort_colors.get(i, '#F0F0F0'), zorder=1)
                if i < len(beaufort_breaks):
                    ax.axhline(y=beaufort_breaks[i], color='gray', alpha=0.3, linewidth=0.5, linestyle='--', zorder=2)
        # Wind speed line
        line_widths = [2 + (ws / max(wind_speed) * 3) if max(wind_speed) > 0 else 3 for ws in wind_speed]
        for i in range(len(dates)-1):
            ax.plot(
                dates[i:i+2], wind_speed[i:i+2],
                color=self.colors['wind'][1],
                linewidth=line_widths[i] * self.scale,
                alpha=0.8,
                zorder=5
            )
        # Wind speed markers
        scatter = ax.scatter(
            dates, wind_speed,
            c=wind_speed,
            cmap='YlOrRd',
            s=[100 + ws*20 for ws in wind_speed],
            edgecolor='white',
            linewidth=1.5 * self.scale,
            zorder=6,
            alpha=0.9
        )
        # Wind direction
        if show_direction and not simplify:
            ax2 = ax.twinx()
            compass_points = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
            compass_angles = [0, 45, 90, 135, 180, 225, 270, 315]
            wind_directions = []
            for deg in wind_deg:
                idx = min(range(len(compass_angles)), key=lambda i: abs(compass_angles[i] - deg))
                wind_directions.append(compass_points[idx])
            for i, (date, direction, speed) in enumerate(zip(dates, wind_directions, wind_speed)):
                ax2.text(
                    date, speed, direction,
                    ha='center', va='center',
                    fontsize=9 * self.scale,
                    fontweight='bold',
                    color=self.colors['text'],
                    bbox=dict(boxstyle='circle,pad=0.3', facecolor='white', alpha=0.8, edgecolor=self.colors['wind'][1])
                )
            ax2.set_ylim(ax.get_ylim())
            ax2.set_ylabel('Wind Direction', fontsize=self.chart_config['label_fontsize'] - 2, color=self.colors['text'])
            ax2.tick_params(axis='y', labelcolor=self.colors['text'])
        # Formatting
        self._format_responsive_chart(ax, weather_data, 'wind', title)
        ax.set_ylabel(f"Wind Speed ({weather_data['units']['speed']})", fontsize=self.chart_config['label_fontsize'], color=self.colors['text'], fontweight='bold')
        # Wind statistics
        avg_speed = np.mean(wind_speed)
        max_speed = max(wind_speed)
        prevailing_dir = self._get_prevailing_direction(wind_deg)
        stats_text = f"Avg: {avg_speed:.1f} {weather_data['units']['speed']} | Max: {max_speed:.1f} | Prevailing: {prevailing_dir}"
        ax.text(
            0.02, 0.95, stats_text,
            transform=ax.transAxes,
            fontsize=10 * self.scale,
            bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.9, edgecolor=self.colors['grid'])
        )
        # Colorbar
        cbar = plt.colorbar(scatter, ax=ax)
        cbar.set_label(f'Wind Speed ({weather_data["units"]["speed"]})', fontsize=self.chart_config['label_fontsize'] - 2)
        plt.tight_layout()
        return self._save_responsive_figure(fig)
    def generate_pressure_chart(
        self,
        weather_data: Dict,
        title: Optional[str] = None,
        show_trend: bool = True,
        show_forecast: bool = True,
        simplify: bool = False
    ) -> BytesIO:
        """
        Generate a responsive atmospheric pressure chart with trend analysis.
        Args:
            weather_data: Weather data dictionary.
            title: Chart title (optional).
            show_trend: Show pressure trend line.
            show_forecast: Show weather forecast based on pressure.
            simplify: Simplify chart for small screens.
        Returns:
            Bytes buffer containing PNG image.
        """
        fig, ax = plt.subplots(figsize=self.figsize)
        forecast = weather_data['forecast']
        dates = [entry['datetime'] for entry in forecast]
        pressure = [entry['pressure'] for entry in forecast]
        # Gradient background
        pressure_min, pressure_max = min(pressure), max(pressure)
        for i in range(len(dates)-1):
            x1, x2 = dates[i], dates[i+1]
            p1, p2 = pressure[i], pressure[i+1]
            avg_pressure = (p1 + p2) / 2
            pressure_norm = (avg_pressure - 1000) / 20
            if pressure_norm > 0:
                color = plt.cm.Blues(0.3 + min(pressure_norm * 0.1, 0.3))
            else:
                color = plt.cm.Reds(0.3 + min(-pressure_norm * 0.1, 0.3))
            x1_num = mdates.date2num(x1)
            x2_num = mdates.date2num(x2)
            rect = Rectangle(
                (x1_num, pressure_min - 5),
                x2_num - x1_num,
                pressure_max - pressure_min + 10,
                facecolor=color,
                alpha=0.1,
                edgecolor='none',
                transform=ax.get_xaxis_transform()
            )
            ax.add_patch(rect)
        # Pressure line
        line = ax.plot(
            dates, pressure,
            color=self.colors['pressure'][1],
            linewidth=3 * self.scale,
            marker='s' if not simplify else '',
            markersize=self.chart_config['marker_size'] if not simplify else 0,
            markerfacecolor='white',
            markeredgecolor=self.colors['pressure'][1],
            markeredgewidth=2 if not simplify else 0,
            zorder=5
        )
        # Trend line
        if show_trend and len(pressure) > 2 and not simplify:
            date_nums = mdates.date2num(dates)
            z = np.polyfit(date_nums, pressure, 1)
            p = np.poly1d(z)
            ax.plot(
                dates, p(date_nums),
                color='red' if z[0] < 0 else 'green',
                linewidth=2 * self.scale,
                linestyle='--',
                alpha=0.7,
                label=f'Trend: {"Falling" if z[0] < 0 else "Rising"}',
                zorder=4
            )
        # Pressure change arrows
        if not simplify:
            for i in range(len(pressure)-1):
                if abs(pressure[i+1] - pressure[i]) > 0.5:
                    x_mid = dates[i] + (dates[i+1] - dates[i]) / 2
                    y_mid = (pressure[i] + pressure[i+1]) / 2
                    if pressure[i+1] > pressure[i]:
                        ax.annotate('', xy=(x_mid, y_mid + 1), xytext=(x_mid, y_mid - 1), arrowprops=dict(arrowstyle='->', color='green', lw=2))
                    else:
                        ax.annotate('', xy=(x_mid, y_mid - 1), xytext=(x_mid, y_mid + 1), arrowprops=dict(arrowstyle='->', color='red', lw=2))
        # Average pressure line
        avg_pressure = np.mean(pressure)
        ax.axhline(
            y=avg_pressure,
            color='black',
            linestyle='--',
            linewidth=1.5 * self.scale,
            alpha=0.7,
            label=f'Average: {avg_pressure:.1f} hPa',
            zorder=3
        )
        # Formatting
        self._format_responsive_chart(ax, weather_data, 'pressure', title)
        ax.set_ylabel(f"Pressure ({weather_data['units']['pressure']})", fontsize=self.chart_config['label_fontsize'], color=self.colors['text'], fontweight='bold')
        # Pressure analysis
        pressure_change = pressure[-1] - pressure[0]
        pressure_trend = "Falling" if pressure_change < 0 else "Rising"
        forecast_text = ""
        if show_forecast:
            if pressure_change < -2:
                forecast_text = "Expect deteriorating weather"
            elif pressure_change > 2:
                forecast_text = "Expect improving weather"
            else:
                forecast_text = "Stable weather conditions"
        stats_text = f"Change: {pressure_change:+.1f} hPa ({pressure_trend})"
        if forecast_text:
            stats_text += f" | {forecast_text}"
        ax.text(
            0.02, 0.95, stats_text,
            transform=ax.transAxes,
            fontsize=10 * self.scale,
            fontweight='bold' if abs(pressure_change) > 3 else 'normal',
            color='red' if pressure_change < -3 else ('green' if pressure_change > 3 else 'black'),
            bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.9, edgecolor=self.colors['grid'])
        )
        plt.tight_layout()
        return self._save_responsive_figure(fig)
    def generate_composite_chart(
        self,
        weather_data: Dict,
        title: Optional[str] = None,
        variables: List[str] = None,
        show_correlation: bool = True,
        simplify: bool = False
    ) -> BytesIO:
        """
        Generate a responsive composite chart with correlation analysis.
        Args:
            weather_data: Weather data dictionary.
            title: Chart title (optional).
            variables: List of variables to include.
            show_correlation: Show correlation between variables.
            simplify: Simplify chart for small screens.
        Returns:
            Bytes buffer containing PNG image.
        """
        if variables is None:
            variables = ['temperature', 'humidity', 'rainfall']
        fig, ax1 = plt.subplots(figsize=(16 * self.scale, 10 * self.scale))
        forecast = weather_data['forecast']
        dates = [entry['datetime'] for entry in forecast]
        # Temperature
        if 'temperature' in variables:
            temps = [entry['temperature'] for entry in forecast]
            line1 = ax1.plot(
                dates, temps,
                color=self.colors['temperature'][1],
                linewidth=3 * self.scale,
                label='Temperature',
                marker='o' if not simplify else '',
                markersize=6 * self.scale if not simplify else 0,
                zorder=5
            )
            ax1.set_ylabel(
                f"Temperature ({weather_data['units']['temperature']})",
                color=self.colors['temperature'][1],
                fontsize=self.chart_config['label_fontsize'],
                fontweight='bold'
            )
            ax1.tick_params(axis='y', labelcolor=self.colors['temperature'][1])
        # Humidity/Rainfall
        ax2 = None
        if 'humidity' in variables or 'rainfall' in variables:
            ax2 = ax1.twinx()
            if 'humidity' in variables:
                humidity = [entry['humidity'] for entry in forecast]
                line2 = ax2.plot(
                    dates, humidity,
                    color=self.colors['humidity'][1],
                    linewidth=2.5 * self.scale,
                    linestyle='--',
                    label='Humidity',
                    marker='s' if not simplify else '',
                    markersize=5 * self.scale if not simplify else 0,
                    zorder=4
                )
                ax2.set_ylabel('Humidity (%)', color=self.colors['humidity'][1], fontsize=self.chart_config['label_fontsize'], fontweight='bold')
                ax2.tick_params(axis='y', labelcolor=self.colors['humidity'][1])
                ax2.set_ylim(0, 105)
            if 'rainfall' in variables:
                rainfall = [entry['rainfall'] for entry in forecast]
                # Calculate the time interval between dates (in days)
                date_interval = (dates[-1] - dates[0]).total_seconds() / (86400 * (len(dates) - 1))
                # Set bar width to 40% of the interval
                bar_width = 0.4 * date_interval
                bars = ax2.bar(
                    dates, rainfall,
                    color=self.colors['rainfall'][1],
                    alpha=0.5,
                    width=bar_width,
                    label='Rainfall',
                    zorder=3
                )
                if not simplify:
                    for bar, rain in zip(bars, rainfall):
                        if rain > 0.5:
                            height = bar.get_height()
                            ax2.text(
                                bar.get_x() + bar.get_width()/2., height + 0.1,
                                f'{rain:.1f}',
                                ha='center', va='bottom',
                                fontsize=8 * self.scale,
                                fontweight='bold'
                            )
                if 'humidity' not in variables:
                    ax2.set_ylabel(
                        f"Rainfall ({weather_data['units']['rainfall']})",
                        color=self.colors['rainfall'][1],
                        fontsize=self.chart_config['label_fontsize'],
                        fontweight='bold'
                    )
                    ax2.tick_params(axis='y', labelcolor=self.colors['rainfall'][1])
        # Wind/Pressure
        ax3 = None
        if 'wind' in variables or 'pressure' in variables:
            ax3 = ax1.twinx()
            ax3.spines['right'].set_position(('outward', 60))
            if 'wind' in variables:
                wind_speed = [entry['wind_speed'] for entry in forecast]
                line3 = ax3.plot(
                    dates, wind_speed,
                    color=self.colors['wind'][1],
                    linewidth=2 * self.scale,
                    linestyle=':',
                    label='Wind Speed',
                    marker='^' if not simplify else '',
                    markersize=4 * self.scale if not simplify else 0,
                    zorder=2
                )
                ax3.set_ylabel(
                    f"Wind Speed ({weather_data['units']['speed']})",
                    color=self.colors['wind'][1],
                    fontsize=self.chart_config['label_fontsize'] - 1
                )
                ax3.tick_params(axis='y', labelcolor=self.colors['wind'][1])
        # Formatting
        location = weather_data['location']
        default_title = f"Weather Analysis: {location['city']}, {location['country']}"
        ax1.set_title(
            title or default_title,
            fontsize=self.chart_config['title_fontsize'] + 2,
            fontweight='bold',
            pad=25,
            color=self.colors['text']
        )
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%b %d\n%H:%M' if self.scale >= 1.0 else '%b %d'))
        ax1.xaxis.set_major_locator(mdates.AutoDateLocator(maxticks=10 if self.scale >= 1.0 else 5))
        ax1.grid(True, alpha=self.chart_config['grid_alpha'], zorder=1)
        ax1.set_xlabel('Date & Time', fontsize=self.chart_config['label_fontsize'], color=self.colors['text'], fontweight='bold')
        # Legends
        lines, labels = [], []
        for ax in [ax1, ax2, ax3]:
            if ax is not None:
                ax_lines, ax_labels = ax.get_legend_handles_labels()
                lines.extend(ax_lines)
                labels.extend(ax_labels)
        ax1.legend(lines, labels, loc='upper left', fontsize=self.chart_config['legend_fontsize'], framealpha=0.9, edgecolor=self.colors['grid'])
        # Correlation
        if show_correlation and len(variables) >= 2 and not simplify:
            corr_text = self._calculate_correlations(weather_data, variables)
            ax1.text(
                0.02, 0.02, corr_text,
                transform=ax1.transAxes,
                fontsize=9 * self.scale,
                bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.9, edgecolor=self.colors['grid'])
            )
        plt.tight_layout()
        return self._save_responsive_figure(fig)
    def _format_responsive_chart(
        self,
        ax: Axes,
        weather_data: Dict,
        chart_type: str,
        title: Optional[str] = None
    ) -> None:
        """Apply responsive formatting to the chart."""
        location = weather_data['location']
        # Title
        if title:
            ax.set_title(
                title,
                fontsize=self.chart_config['title_fontsize'],
                fontweight='bold',
                pad=20,
                color=self.colors['text']
            )
        else:
            chart_titles = {
                'temperature': f"Temperature Forecast: {location['city']}, {location['country']}",
                'humidity': f"Humidity Analysis: {location['city']}, {location['country']}",
                'rainfall': f"Rainfall Forecast: {location['city']}, {location['country']}",
                'wind': f"Wind Conditions: {location['city']}, {location['country']}",
                'pressure': f"Atmospheric Pressure: {location['city']}, {location['country']}"
            }
            ax.set_title(
                chart_titles.get(chart_type, 'Weather Analysis'),
                fontsize=self.chart_config['title_fontsize'],
                fontweight='bold',
                pad=20,
                color=self.colors['text']
            )
        # X-axis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d\n%H:%M' if self.scale >= 1.0 else '%b %d'))
        ax.xaxis.set_major_locator(mdates.AutoDateLocator(maxticks=10 if self.scale >= 1.0 else 5))
        plt.xticks(rotation=45 if self.scale >= 1.0 else 30)
        # Labels and grid
        ax.set_xlabel(
            'Date & Time',
            fontsize=self.chart_config['label_fontsize'],
            color=self.colors['text'],
            fontweight='bold'
        )
        ax.grid(True, alpha=self.chart_config['grid_alpha'], zorder=1)
        ax.tick_params(
            axis='both',
            labelsize=self.chart_config['tick_fontsize'],
            colors=self.colors['text']
        )
        # Background
        ax.set_facecolor(self.colors['background'])
        ax.figure.patch.set_facecolor('white')
        # Border
        for spine in ax.spines.values():
            spine.set_edgecolor(self.colors['grid'])
            spine.set_linewidth(1.5)
    def _save_responsive_figure(self, fig: Figure) -> BytesIO:
        """Save the figure with responsive DPI and quality."""
        buf = BytesIO()
        fig.savefig(
            buf,
            format='png',
            dpi=self.chart_config['dpi'],
            bbox_inches='tight',
            facecolor=fig.get_facecolor(),
            edgecolor='none',
            pad_inches=0.3
        )
        plt.close(fig)
        buf.seek(0)
        return buf
    def _get_humidity_color(self, humidity: float) -> str:
        """Get color based on humidity level."""
        if humidity < 30:
            return '#FFD700'
        elif humidity < 40:
            return '#FFC107'
        elif humidity <= 60:
            return self.colors['success']
        elif humidity <= 70:
            return '#FF9800'
        else:
            return self.colors['danger']
    def _get_rainfall_color(self, rainfall: float) -> str:
        """Get color based on rainfall intensity."""
        if rainfall == 0:
            return '#E3F2FD'
        elif rainfall < 1:
            return '#90CAF9'
        elif rainfall < 5:
            return '#42A5F5'
        elif rainfall < 10:
            return '#1E88E5'
        else:
            return '#0D47A1'
    def _get_prevailing_direction(self, degrees: List[float]) -> str:
        """Calculate prevailing wind direction."""
        if not degrees:
            return "N/A"
        compass_points = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']
        direction_counts = {dir: 0 for dir in compass_points}
        for deg in degrees:
            idx = int((deg + 11.25) / 22.5) % 16
            direction_counts[compass_points[idx]] += 1
        return max(direction_counts, key=direction_counts.get)
    def _calculate_correlations(self, weather_data: Dict, variables: List[str]) -> str:
        """Calculate correlations between weather variables."""
        forecast = weather_data['forecast']
        data_dict = {}
        if 'temperature' in variables:
            data_dict['temp'] = [entry['temperature'] for entry in forecast]
        if 'humidity' in variables:
            data_dict['humidity'] = [entry['humidity'] for entry in forecast]
        if 'rainfall' in variables:
            data_dict['rain'] = [entry['rainfall'] for entry in forecast]
        if 'wind' in variables:
            data_dict['wind'] = [entry['wind_speed'] for entry in forecast]
        if 'pressure' in variables:
            data_dict['pressure'] = [entry['pressure'] for entry in forecast]
        correlations = []
        variable_names = list(data_dict.keys())
        for i in range(len(variable_names)):
            for j in range(i+1, len(variable_names)):
                var1 = variable_names[i]
                var2 = variable_names[j]
                if len(data_dict[var1]) == len(data_dict[var2]):
                    corr = np.corrcoef(data_dict[var1], data_dict[var2])[0, 1]
                    if not np.isnan(corr):
                        corr_text = f"{var1[:3]}-{var2[:3]}: {corr:.2f}"
                        if abs(corr) > 0.7:
                            corr_text += " (Strong)"
                        elif abs(corr) > 0.4:
                            corr_text += " (Moderate)"
                        else:
                            corr_text += " (Weak)"
                        correlations.append(corr_text)
        return "Correlations: " + " | ".join(correlations[:3]) if correlations else ""