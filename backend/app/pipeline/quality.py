"""
Data Quality and Anomaly Detection Engine for Weather Records.
Uses Pydantic V2 to enforce meteorological constraints, auto-correct inverted columns,
detect temperature delta anomalies, and sanitize conditions.
"""
from typing import Dict, Any, List, Optional, Tuple
from pydantic import BaseModel, Field, field_validator, model_validator
import logging

logger = logging.getLogger(__name__)

# Extreme climate bounds for Ethiopia
ETHIOPIA_MIN_TEMP_LOWER_BOUND = -10  # Even Bale/Ras Dashen rarely drops below -8C
ETHIOPIA_MAX_TEMP_UPPER_BOUND = 55   # Even Danakil/Dallol peak is ~50C
MAX_DAY_OVER_DAY_JUMP = 18           # >18C swing within 24h is an anomaly in the tropics


class ValidatedDayForecast(BaseModel):
    min_temp: int
    max_temp: int
    condition: str
    rain_percent: int = Field(default=0, ge=0, le=100)
    wind: int = Field(default=0, ge=0)

    @field_validator("condition", mode="before")
    @classmethod
    def sanitize_condition(cls, v: Any) -> str:
        if not v or not str(v).strip():
            return "Partly Cloudy"
        val = str(v).strip().title()
        return val


class ValidatedForecastRecord(BaseModel):
    city: str
    data_source: str = "NMA"
    quality_status: str = "verified"  # "verified", "corrected", "fallback", "anomaly"
    anomalies: List[str] = Field(default_factory=list)

    min_temp_d1: int
    max_temp_d1: int
    condition_d1: str
    rain_percent_d1: int = 0
    wind_d1: int = 0

    min_temp_d2: int
    max_temp_d2: int
    condition_d2: str
    rain_percent_d2: int = 0
    wind_d2: int = 0

    min_temp_d3: int
    max_temp_d3: int
    condition_d3: str
    rain_percent_d3: int = 0
    wind_d3: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to database-compatible dictionary format."""
        return {
            "City": self.city,
            "MinTempD1": self.min_temp_d1,
            "MaxTempD1": self.max_temp_d1,
            "WeatherConditionD1": self.condition_d1,
            "RainPercentD1": self.rain_percent_d1,
            "WindD1": self.wind_d1,
            "MinTempD2": self.min_temp_d2,
            "MaxTempD2": self.max_temp_d2,
            "WeatherConditionD2": self.condition_d2,
            "RainPercentD2": self.rain_percent_d2,
            "WindD2": self.wind_d2,
            "MinTempD3": self.min_temp_d3,
            "MaxTempD3": self.max_temp_d3,
            "WeatherConditionD3": self.condition_d3,
            "RainPercentD3": self.rain_percent_d3,
            "WindD3": self.wind_d3,
            "DataSource": self.data_source,
            "QualityStatus": self.quality_status,
        }


class QualityReport(BaseModel):
    total_inspected: int = 0
    verified: int = 0
    corrected: int = 0
    rejected: int = 0
    anomalies_detected: List[Dict[str, Any]] = Field(default_factory=list)


def validate_and_clean_record(raw: Dict[str, Any]) -> Tuple[Optional[ValidatedForecastRecord], List[str]]:
    """
    Validates a single raw weather record.
    Performs temperature sanity checking, inversion correction, and delta jump detection.
    Returns (validated_record, list_of_anomalies).
    """
    anomalies: List[str] = []
    is_corrected = False

    city = raw.get("City") or raw.get("city")
    if not city or not str(city).strip():
        return None, ["Missing or empty city name"]

    city = str(city).strip()
    data_source = raw.get("DataSource") or raw.get("data_source") or "NMA"

    try:
        # Day 1
        min_d1 = int(raw.get("MinTempD1", raw.get("min_temp_d1", 0)))
        max_d1 = int(raw.get("MaxTempD1", raw.get("max_temp_d1", 0)))
        cond_d1 = str(raw.get("WeatherConditionD1", raw.get("condition_d1", "Partly Cloudy"))).strip()
        rain_d1 = max(0, min(100, int(raw.get("RainPercentD1", raw.get("rain_percent_d1", 0) or 0))))
        wind_d1 = max(0, int(raw.get("WindD1", raw.get("wind_d1", 0) or 0)))

        # Day 2
        min_d2 = int(raw.get("MinTempD2", raw.get("min_temp_d2", 0)))
        max_d2 = int(raw.get("MaxTempD2", raw.get("max_temp_d2", 0)))
        cond_d2 = str(raw.get("WeatherConditionD2", raw.get("condition_d2", "Partly Cloudy"))).strip()
        rain_d2 = max(0, min(100, int(raw.get("RainPercentD2", raw.get("rain_percent_d2", 0) or 0))))
        wind_d2 = max(0, int(raw.get("WindD2", raw.get("wind_d2", 0) or 0)))

        # Day 3
        min_d3 = int(raw.get("MinTempD3", raw.get("min_temp_d3", 0)))
        max_d3 = int(raw.get("MaxTempD3", raw.get("max_temp_d3", 0)))
        cond_d3 = str(raw.get("WeatherConditionD3", raw.get("condition_d3", "Partly Cloudy"))).strip()
        rain_d3 = max(0, min(100, int(raw.get("RainPercentD3", raw.get("rain_percent_d3", 0) or 0))))
        wind_d3 = max(0, int(raw.get("WindD3", raw.get("wind_d3", 0) or 0)))

    except (ValueError, TypeError) as err:
        return None, [f"Invalid numerical temperature format: {err}"]

    # Check 1: Inverted Temperatures (min > max) -> Auto-Correct
    for day_num, (mn, mx) in enumerate([(min_d1, max_d1), (min_d2, max_d2), (min_d3, max_d3)], start=1):
        if mn > mx:
            anomalies.append(f"Day {day_num}: Inverted temperatures ({mn}°C > {mx}°C) - auto-swapped")
            is_corrected = True
            if day_num == 1:
                min_d1, max_d1 = mx, mn
            elif day_num == 2:
                min_d2, max_d2 = mx, mn
            else:
                min_d3, max_d3 = mx, mn

    # Check 2: Absolute Meteorological Range
    for day_num, (mn, mx) in enumerate([(min_d1, max_d1), (min_d2, max_d2), (min_d3, max_d3)], start=1):
        if mn < ETHIOPIA_MIN_TEMP_LOWER_BOUND or mx > ETHIOPIA_MAX_TEMP_UPPER_BOUND:
            anomalies.append(f"Day {day_num}: Extreme temperature out-of-bounds ({mn}°C to {mx}°C)")
            # If impossible values, reject
            if mn < -20 or mx > 65:
                return None, [f"Unrealistic meteorological temperature ({mn}°C, {mx}°C) in Ethiopia"]

    # Check 3: Sudden Delta Spike between consecutive days
    if abs(max_d2 - max_d1) > MAX_DAY_OVER_DAY_JUMP:
        anomalies.append(f"Sudden temperature jump between Day 1 ({max_d1}°C) and Day 2 ({max_d2}°C)")
    if abs(max_d3 - max_d2) > MAX_DAY_OVER_DAY_JUMP:
        anomalies.append(f"Sudden temperature jump between Day 2 ({max_d2}°C) and Day 3 ({max_d3}°C)")

    # Assign Quality Status
    if data_source.lower() == "open-meteo":
        quality_status = "fallback"
    elif is_corrected:
        quality_status = "corrected"
    elif anomalies:
        quality_status = "flagged_anomaly"
    else:
        quality_status = "verified"

    record = ValidatedForecastRecord(
        city=city,
        data_source=data_source,
        quality_status=quality_status,
        anomalies=anomalies,
        min_temp_d1=min_d1,
        max_temp_d1=max_d1,
        condition_d1=cond_d1 or "Partly Cloudy",
        rain_percent_d1=rain_d1,
        wind_d1=wind_d1,
        min_temp_d2=min_d2,
        max_temp_d2=max_d2,
        condition_d2=cond_d2 or "Partly Cloudy",
        rain_percent_d2=rain_d2,
        wind_d2=wind_d2,
        min_temp_d3=min_d3,
        max_temp_d3=max_d3,
        condition_d3=cond_d3 or "Partly Cloudy",
        rain_percent_d3=rain_d3,
        wind_d3=wind_d3,
    )

    return record, anomalies


def validate_batch(records: List[Dict[str, Any]]) -> Tuple[List[ValidatedForecastRecord], QualityReport]:
    """
    Validates a batch of records and generates a quality summary report.
    """
    validated_list: List[ValidatedForecastRecord] = []
    report = QualityReport(total_inspected=len(records))

    for raw in records:
        valid_rec, anomalies = validate_and_clean_record(raw)
        if not valid_rec:
            report.rejected += 1
            report.anomalies_detected.append({
                "city": raw.get("City", "Unknown"),
                "reason": anomalies,
                "action": "rejected"
            })
            continue

        if valid_rec.quality_status == "corrected":
            report.corrected += 1
            report.anomalies_detected.append({
                "city": valid_rec.city,
                "anomalies": anomalies,
                "action": "auto_corrected"
            })
        elif valid_rec.quality_status in ("verified", "fallback"):
            report.verified += 1

        validated_list.append(valid_rec)

    return validated_list, report
