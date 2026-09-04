"""
Weather alert detection logic.
Detects extreme weather conditions and generates alerts.
"""
from typing import List
from .models import WeatherAlert, AlertLevel, CityForecast


# Alert thresholds
EXTREME_HEAT_THRESHOLD = 35  # Celsius
EXTREME_COLD_THRESHOLD = 5   # Celsius
HEAVY_RAIN_THRESHOLD = 60    # Percentage
HAZARDOUS_CONDITIONS = ["thunderstorm", "heavy rain", "hail", "tornado"]


def detect_alerts(city: CityForecast) -> List[WeatherAlert]:
    """
    Detects extreme weather conditions for a city.
    
    Args:
        city: CityForecast object containing forecast data
        
    Returns:
        List of WeatherAlert objects
    """
    alerts = []
    
    if not city.days:
        return alerts
    
    today = city.days[0]
    
    # Check for extreme heat
    if today.max >= EXTREME_HEAT_THRESHOLD:
        alerts.append(WeatherAlert(
            city_name=city.name,
            level=AlertLevel.CRITICAL if today.max >= 40 else AlertLevel.WARNING,
            message=f"Extreme heat warning: Temperature expected to reach {today.max}°C",
            trigger="extreme_heat",
            value=float(today.max)
        ))
    
    # Check for extreme cold
    if today.min <= EXTREME_COLD_THRESHOLD:
        alerts.append(WeatherAlert(
            city_name=city.name,
            level=AlertLevel.WARNING,
            message=f"Cold weather warning: Temperature expected to drop to {today.min}°C",
            trigger="extreme_cold",
            value=float(today.min)
        ))
    
    # Check for heavy rain
    rain_percent = today.rain_percent or 0
    if rain_percent >= HEAVY_RAIN_THRESHOLD:
        alerts.append(WeatherAlert(
            city_name=city.name,
            level=AlertLevel.WARNING if rain_percent >= 80 else AlertLevel.INFO,
            message=f"Heavy rain expected with {rain_percent}% probability",
            trigger="heavy_rain",
            value=float(rain_percent)
        ))
    
    # Check for hazardous conditions
    condition_lower = today.condition.lower()
    for hazard in HAZARDOUS_CONDITIONS:
        if hazard in condition_lower:
            alerts.append(WeatherAlert(
                city_name=city.name,
                level=AlertLevel.CRITICAL,
                message=f"Hazardous weather alert: {today.condition}",
                trigger="hazardous_condition",
                value=0
            ))
            break  # Only add one hazardous condition alert
    
    return alerts


def detect_all_alerts(cities: List[CityForecast]) -> List[WeatherAlert]:
    """
    Detects alerts for all cities.
    
    Args:
        cities: List of CityForecast objects
        
    Returns:
        Combined list of all alerts, sorted by severity
    """
    all_alerts = []
    for city in cities:
        all_alerts.extend(detect_alerts(city))
    
    # Sort by severity: critical > warning > info
    severity_order = {AlertLevel.CRITICAL: 0, AlertLevel.WARNING: 1, AlertLevel.INFO: 2}
    all_alerts.sort(key=lambda a: severity_order.get(a.level, 3))
    
    return all_alerts
