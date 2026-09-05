"""
Ethiopian Agro-Meteorological and Seasonal Advisory Engine.
Evaluates weather forecasts against Ethiopian seasonal regimes (Kiremt, Bega, Belg)
and generates actionable advisories for key agricultural sectors (Teff, Coffee, Wheat, Livestock).
"""
from datetime import datetime
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

from .regions import region_for
from .pipeline.cities import get_city_coords


class CropAdvisory(BaseModel):
    crop_name: str
    amharic_name: str
    status: str  # "Favorable", "Caution", "Alert"
    headline: str
    recommendation: str
    risk_level: str  # "low", "medium", "high"


class SeasonalProfile(BaseModel):
    season_name: str
    amharic_name: str
    description: str
    progress_percentage: int
    days_remaining: int
    primary_activities: List[str]


class CityAgroAdvisory(BaseModel):
    city_name: str
    region: str
    elevation: int
    agro_climatic_zone: str  # Dega (>2300m), Weyna Dega (1500-2300m), Kolla (<1500m), Bereha (<500m)
    current_season: SeasonalProfile
    crop_advisories: List[CropAdvisory]
    frost_alert: bool = False
    waterlogging_risk: bool = False
    heat_stress_alert: bool = False


def get_agro_climatic_zone(elevation: int) -> str:
    """Classifies elevation into traditional Ethiopian agro-climatic zones."""
    if elevation >= 2300:
        return "Dega (Highland Cool, >2,300m)"
    elif elevation >= 1500:
        return "Weyna Dega (Midland Temperate, 1,500–2,300m)"
    elif elevation >= 500:
        return "Kolla (Lowland Warm, 500–1,500m)"
    else:
        return "Bereha (Hot Arid, <500m)"


def calculate_current_season(dt: Optional[datetime] = None) -> SeasonalProfile:
    """Calculates active Ethiopian agricultural season and timeline."""
    now = dt or datetime.utcnow()
    month = now.month
    day = now.day

    # Kiremt (June 15 - September 30): Main summer rainy season
    if (month == 6 and day >= 15) or (month in [7, 8]) or (month == 9):
        start = datetime(now.year, 6, 15)
        end = datetime(now.year, 9, 30)
        total_days = (end - start).days
        elapsed = max(0, (now - start).days)
        progress = min(100, int((elapsed / total_days) * 100))
        days_rem = max(0, (end - now).days)
        return SeasonalProfile(
            season_name="Kiremt",
            amharic_name="ክረምት",
            description="Main rainy season. Critical period for Meher crops (Teff, Maize, Sorghum, Wheat).",
            progress_percentage=progress,
            days_remaining=days_rem,
            primary_activities=[
                "Weeding and fertilizer application for Meher crops",
                "Drainage management in vertisol highlands",
                "Water harvesting and pond maintenance"
            ]
        )

    # Bega (October 1 - January 31): Dry harvest season, cold nights
    elif (month in [10, 11, 12]) or (month == 1):
        year_start = now.year if month in [10, 11, 12] else now.year - 1
        start = datetime(year_start, 10, 1)
        end = datetime(year_start + 1, 1, 31)
        total_days = (end - start).days
        elapsed = max(0, (now - start).days)
        progress = min(100, int((elapsed / total_days) * 100))
        days_rem = max(0, (end - now).days)
        return SeasonalProfile(
            season_name="Bega",
            amharic_name="በጋ",
            description="Dry harvest season. Sunny days with cold highland nights and frost risks.",
            progress_percentage=progress,
            days_remaining=days_rem,
            primary_activities=[
                "Harvesting and threshing of Teff and cereals",
                "Coffee cherry picking and patio sun-drying",
                "Frost protection in highland plateaus"
            ]
        )

    # Belg (February 1 - June 14): Short rainy season
    else:
        start = datetime(now.year, 2, 1)
        end = datetime(now.year, 6, 14)
        total_days = (end - start).days
        elapsed = max(0, (now - start).days)
        progress = min(100, int((elapsed / total_days) * 100))
        days_rem = max(0, (end - now).days)
        return SeasonalProfile(
            season_name="Belg",
            amharic_name="በልግ",
            description="Short rainy season. Crucial for secondary Belg crops and pastoralist rangeland rejuvenation.",
            progress_percentage=progress,
            days_remaining=days_rem,
            primary_activities=[
                "Land preparation and sowing of Belg crops",
                "Replenishment of pastoralist water ponds and grazing pastures",
                "Coffee tree rejuvenation and flowering support"
            ]
        )


def evaluate_crop_advisories(city_name: str, forecast_day: Dict[str, Any], elevation: int) -> List[CropAdvisory]:
    """Generates agro-meteorological advisories based on city microclimate and 3-day forecast."""
    min_temp = forecast_day.get("min", 12)
    max_temp = forecast_day.get("max", 24)
    rain_pct = forecast_day.get("rain_percent", 0) or 0
    condition = forecast_day.get("condition", "Partly Cloudy").lower()
    region = region_for(city_name)
    advisories = []

    # 1. Teff (ጤፍ) Advisory
    if rain_pct >= 70 or "thunderstorm" in condition or "heavy rain" in condition:
        advisories.append(CropAdvisory(
            crop_name="Teff",
            amharic_name="ጤፍ",
            status="Caution",
            headline="Heavy Precipitation & Waterlogging Risk",
            recommendation="Clear drainage furrows in vertisol fields to avoid root rot. Postpone herbicide spraying and grain threshing.",
            risk_level="medium"
        ))
    elif rain_pct <= 20 and max_temp >= 20:
        advisories.append(CropAdvisory(
            crop_name="Teff",
            amharic_name="ጤፍ",
            status="Favorable",
            headline="Optimal Harvesting & Sowing Window",
            recommendation="Dry, sunny conditions favor open-field weeding, grain curing, and mechanized threshing.",
            risk_level="low"
        ))
    else:
        advisories.append(CropAdvisory(
            crop_name="Teff",
            amharic_name="ጤፍ",
            status="Favorable",
            headline="Moderate Vegetative Moisture",
            recommendation="Soil moisture is adequate for ongoing tillering. Monitor seedling stands.",
            risk_level="low"
        ))

    # 2. Coffee Arabica (ቡና) Advisory
    is_coffee_belt = any(k in region.lower() or k in city_name.lower() for k in ["southwestern", "rift", "jimma", "hawassa", "arba minch"])
    if is_coffee_belt:
        if rain_pct <= 25 and max_temp >= 22:
            advisories.append(CropAdvisory(
                crop_name="Coffee Arabica",
                amharic_name="ቡና",
                status="Favorable",
                headline="Excellent Sun-Drying Weather",
                recommendation="Sun-drying parchment and natural cherries on raised African beds will proceed rapidly without mould risk.",
                risk_level="low"
            ))
        elif rain_pct >= 60:
            advisories.append(CropAdvisory(
                crop_name="Coffee Arabica",
                amharic_name="ቡና",
                status="Caution",
                headline="High Humidity & Berry Disease Risk",
                recommendation="Cover drying beds with plastic tarps during rain hours. Inspect plantations for Coffee Berry Disease (CBD) spores.",
                risk_level="medium"
            ))
        else:
            advisories.append(CropAdvisory(
                crop_name="Coffee Arabica",
                amharic_name="ቡና",
                status="Favorable",
                headline="Good Vegetative & Berry Swelling Conditions",
                recommendation="Intermittent cloud cover reduces transpiration stress on shaded coffee bushes.",
                risk_level="low"
            ))

    # 3. Wheat & Barley (ስንዴና ገብስ) Advisory
    if min_temp <= 5 and elevation >= 2200:
        advisories.append(CropAdvisory(
            crop_name="Highland Wheat & Barley",
            amharic_name="ስንዴና ገብስ",
            status="Alert",
            headline="Highland Frost Warning (ውርጭ)",
            recommendation=f"Night temperature expected to plummet to {min_temp}°C in {city_name}. Consider light evening furrow irrigation or smoke smudging to protect flowering grain heads.",
            risk_level="high"
        ))
    elif rain_pct >= 65 and max_temp >= 24:
        advisories.append(CropAdvisory(
            crop_name="Highland Wheat & Barley",
            amharic_name="ስንዴና ገብስ",
            status="Caution",
            headline="Wheat Stem & Yellow Rust Alert",
            recommendation="Warm humid weather promotes rapid fungal spore propagation. Scout wheat canopies for orange pustules.",
            risk_level="medium"
        ))
    else:
        advisories.append(CropAdvisory(
            crop_name="Highland Wheat & Barley",
            amharic_name="ስንዴና ገብስ",
            status="Favorable",
            headline="Normal Growth Regime",
            recommendation="Temperatures within optimal range for grain filling.",
            risk_level="low"
        ))

    # 4. Pastoralist / Livestock Advisory (Afar, Somali, Lowlands)
    is_lowland = elevation < 1600 or any(k in region.lower() for k in ["afar", "eastern", "lowland"])
    if is_lowland:
        if max_temp >= 38:
            advisories.append(CropAdvisory(
                crop_name="Pastoralist Livestock",
                amharic_name="የከብት እርባታ",
                status="Alert",
                headline="Extreme Livestock Heat Stress",
                recommendation=f"Daytime heat peaking at {max_temp}°C. Move camel and cattle herds to acacia shade during 11:00–15:00 and prioritize watering troughs.",
                risk_level="high"
            ))
        elif rain_pct >= 50:
            advisories.append(CropAdvisory(
                crop_name="Pastoralist Livestock",
                amharic_name="የከብት እርባታ",
                status="Favorable",
                headline="Rangeland & Water Pond Replenishment",
                recommendation="Expected precipitation will regenerate browse pastures and fill shallow earthen ponds (birkas).",
                risk_level="low"
            ))
        else:
            advisories.append(CropAdvisory(
                crop_name="Pastoralist Livestock",
                amharic_name="የከብት እርባታ",
                status="Favorable",
                headline="Stable Grazing Conditions",
                recommendation="Pasture grazing is standard. Maintain normal herd foraging radii.",
                risk_level="low"
            ))

    return advisories


def generate_city_agro_advisory(city_name: str, forecast_day: Dict[str, Any]) -> CityAgroAdvisory:
    """Generates a complete agro-advisory response for a single city."""
    coords = get_city_coords(city_name) or {}
    elevation = coords.get("elevation", 2000)
    region = region_for(city_name)
    season = calculate_current_season()
    crop_advisories = evaluate_crop_advisories(city_name, forecast_day, elevation)

    min_t = forecast_day.get("min", 12)
    max_t = forecast_day.get("max", 24)
    rain_p = forecast_day.get("rain_percent", 0) or 0

    return CityAgroAdvisory(
        city_name=city_name,
        region=region,
        elevation=elevation,
        agro_climatic_zone=get_agro_climatic_zone(elevation),
        current_season=season,
        crop_advisories=crop_advisories,
        frost_alert=(min_t <= 5 and elevation >= 2200),
        waterlogging_risk=(rain_p >= 70),
        heat_stress_alert=(max_t >= 38)
    )

