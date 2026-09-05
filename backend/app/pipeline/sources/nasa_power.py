"""
Tertiary Fallback & Agro-Climatology Provider: NASA POWER API.
(Prediction Of Worldwide Energy Resources - Agroclimatology)
Provides satellite and reanalysis meteorological feeds for Ethiopian coordinates.
Endpoint: https://power.larc.nasa.gov/api/temporal/daily/point
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import requests
from ..cities import get_city_coords

logger = logging.getLogger(__name__)

NASA_POWER_API_URL = "https://power.larc.nasa.gov/api/temporal/daily/point"


def fetch_city_forecast_nasa_power(city_name: str, timeout: int = 12) -> Optional[Dict[str, Any]]:
    """
    Queries NASA POWER for daily meteorological observations and short-term trends for Ethiopian coordinates.
    Parameters fetched:
    - T2M_MAX: Temperature at 2 Meters Maximum (°C)
    - T2M_MIN: Temperature at 2 Meters Minimum (°C)
    - PRECTOTCORR: Precipitation Corrected (mm/day)
    - WS10M: Wind Speed at 10 Meters (m/s)
    """
    coords = get_city_coords(city_name)
    if not coords:
        return None

    # NASA POWER uses YYYYMMDD format
    end_dt = datetime.utcnow()
    start_dt = end_dt - timedelta(days=5)

    params = {
        "parameters": "T2M_MAX,T2M_MIN,PRECTOTCORR,WS10M",
        "community": "AG",
        "longitude": coords["longitude"],
        "latitude": coords["latitude"],
        "start": start_dt.strftime("%Y%m%d"),
        "end": end_dt.strftime("%Y%m%d"),
        "format": "JSON",
    }

    try:
        res = requests.get(NASA_POWER_API_URL, params=params, timeout=timeout)
        if res.status_code != 200:
            logger.warning(f"NASA POWER returned HTTP {res.status_code} for {city_name}")
            return None

        data = res.json()
        props = data.get("properties", {}).get("parameter", {})
        t_max_dict = props.get("T2M_MAX", {})
        t_min_dict = props.get("T2M_MIN", {})
        rain_dict = props.get("PRECTOTCORR", {})
        wind_dict = props.get("WS10M", {})

        if not t_max_dict:
            return None

        recent_dates = sorted(list(t_max_dict.keys()))
        if len(recent_dates) < 3:
            # Duplicate or extrapolate if fewer points
            d1_key = recent_dates[-1]
            d2_key = recent_dates[-1]
            d3_key = recent_dates[-1]
        else:
            d1_key = recent_dates[-1]
            d2_key = recent_dates[-2]
            d3_key = recent_dates[-3]

        def get_val(d, k, default):
            v = d.get(k, default)
            return default if v == -999 else v

        max_1 = int(round(get_val(t_max_dict, d1_key, 22)))
        min_1 = int(round(get_val(t_min_dict, d1_key, 12)))
        rain_1 = min(100, int(round(get_val(rain_dict, d1_key, 0) * 10)))
        wind_1 = int(round(get_val(wind_dict, d1_key, 8)))

        max_2 = int(round(get_val(t_max_dict, d2_key, 23)))
        min_2 = int(round(get_val(t_min_dict, d2_key, 12)))
        rain_2 = min(100, int(round(get_val(rain_dict, d2_key, 0) * 10)))
        wind_2 = int(round(get_val(wind_dict, d2_key, 8)))

        max_3 = int(round(get_val(t_max_dict, d3_key, 22)))
        min_3 = int(round(get_val(t_min_dict, d3_key, 11)))
        rain_3 = min(100, int(round(get_val(rain_dict, d3_key, 0) * 10)))
        wind_3 = int(round(get_val(wind_dict, d3_key, 8)))

        # Determine conditions from rain
        cond_1 = "Rain Showers" if rain_1 > 40 else "Partly Cloudy" if rain_1 > 10 else "Sunny"
        cond_2 = "Rain Showers" if rain_2 > 40 else "Partly Cloudy" if rain_2 > 10 else "Sunny"
        cond_3 = "Rain Showers" if rain_3 > 40 else "Partly Cloudy" if rain_3 > 10 else "Sunny"

        return {
            "City": city_name,
            "MinTempD1": min_1,
            "MaxTempD1": max_1,
            "WeatherConditionD1": cond_1,
            "RainPercentD1": rain_1,
            "WindD1": wind_1,
            "MinTempD2": min_2,
            "MaxTempD2": max_2,
            "WeatherConditionD2": cond_2,
            "RainPercentD2": rain_2,
            "WindD2": wind_2,
            "MinTempD3": min_3,
            "MaxTempD3": max_3,
            "WeatherConditionD3": cond_3,
            "RainPercentD3": rain_3,
            "WindD3": wind_3,
            "DataSource": "NASA-POWER",
        }
    except Exception as err:
        logger.warning(f"NASA POWER query failed for {city_name}: {err}")
        return None

