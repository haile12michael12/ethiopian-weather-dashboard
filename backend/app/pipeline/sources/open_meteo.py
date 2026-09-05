"""
Secondary Fallback Weather Provider: Open-Meteo API.
Provides high-reliability, zero-auth ECMWF/GFS meteorological forecasts for Ethiopian cities.
"""
import logging
from typing import Dict, Any, List, Optional
import requests
from ..cities import ETHIOPIAN_CITIES, get_city_coords

logger = logging.getLogger(__name__)

OPEN_METEO_BASE_URL = "https://api.open-meteo.com/v1/forecast"

# WMO Weather interpretation codes (WW) to Dashboard conditions
WMO_CODE_MAP = {
    0: "Sunny",
    1: "Mostly Sunny",
    2: "Partly Cloudy",
    3: "Cloudy",
    45: "Foggy",
    48: "Foggy",
    51: "Scattered Showers",
    53: "Scattered Showers",
    55: "Rain Showers",
    56: "Rain Showers",
    57: "Rain Showers",
    61: "Rain Showers",
    63: "Rain Showers",
    65: "Heavy Rain",
    66: "Heavy Rain",
    67: "Heavy Rain",
    71: "Rain Showers",
    73: "Rain Showers",
    75: "Rain Showers",
    77: "Scattered Showers",
    80: "Rain Showers",
    81: "Rain Showers",
    82: "Heavy Rain",
    85: "Rain Showers",
    86: "Heavy Rain",
    95: "Thunderstorms",
    96: "Thunderstorms",
    99: "Thunderstorms",
}


def wmo_to_condition(code: Optional[int]) -> str:
    """Translates WMO weather code to standard condition name."""
    if code is None:
        return "Partly Cloudy"
    return WMO_CODE_MAP.get(int(code), "Partly Cloudy")


def fetch_city_forecast_open_meteo(city_name: str, timeout: int = 10) -> Optional[Dict[str, Any]]:
    """
    Fetches 3-day forecast for an Ethiopian city from Open-Meteo.
    """
    coords = get_city_coords(city_name)
    if not coords:
        logger.warning(f"No coordinates registered for city '{city_name}'")
        return None

    params = {
        "latitude": coords["latitude"],
        "longitude": coords["longitude"],
        "daily": "temperature_2m_max,temperature_2m_min,weather_code,precipitation_probability_max,wind_speed_10m_max",
        "timezone": "Africa/Addis_Ababa",
        "forecast_days": 3,
    }

    headers = {
        "User-Agent": "EthiopianWeatherDashboard/2.0 (ResilientPipeline; OpenMeteoFallback)",
        "Accept": "application/json",
    }

    try:
        res = requests.get(OPEN_METEO_BASE_URL, params=params, headers=headers, timeout=timeout)
        res.raise_for_status()
        data = res.json()

        daily = data.get("daily", {})
        max_temps = daily.get("temperature_2m_max", [20, 20, 20])
        min_temps = daily.get("temperature_2m_min", [12, 12, 12])
        codes = daily.get("weather_code", [2, 2, 2])
        rain_probs = daily.get("precipitation_probability_max", [0, 0, 0])
        winds = daily.get("wind_speed_10m_max", [0, 0, 0])

        return {
            "City": city_name,
            "MinTempD1": int(round(min_temps[0])),
            "MaxTempD1": int(round(max_temps[0])),
            "WeatherConditionD1": wmo_to_condition(codes[0]),
            "RainPercentD1": int(round(rain_probs[0] or 0)),
            "WindD1": int(round(winds[0] or 0)),
            "MinTempD2": int(round(min_temps[1])),
            "MaxTempD2": int(round(max_temps[1])),
            "WeatherConditionD2": wmo_to_condition(codes[1]),
            "RainPercentD2": int(round(rain_probs[1] or 0)),
            "WindD2": int(round(winds[1] or 0)),
            "MinTempD3": int(round(min_temps[2])),
            "MaxTempD3": int(round(max_temps[2])),
            "WeatherConditionD3": wmo_to_condition(codes[2]),
            "RainPercentD3": int(round(rain_probs[2] or 0)),
            "WindD3": int(round(winds[2] or 0)),
            "DataSource": "Open-Meteo",
        }
    except Exception as exc:
        logger.error(f"Open-Meteo fallback failed for {city_name}: {exc}")
        return None


def fetch_all_cities_open_meteo(cities: Optional[List[str]] = None, timeout: int = 10) -> List[Dict[str, Any]]:
    """
    Fetches forecasts for all designated Ethiopian cities from Open-Meteo.
    """
    target_cities = cities or list(ETHIOPIAN_CITIES.keys())
    results = []

    for city in target_cities:
        record = fetch_city_forecast_open_meteo(city, timeout=timeout)
        if record:
            results.append(record)

    return results
