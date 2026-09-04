from typing import List, Optional
from enum import Enum
from pydantic import BaseModel
from datetime import datetime


class AlertLevel(str, Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class TrendDirection(str, Enum):
    """Trend direction indicators"""
    RISING = "rising"      # Temperature increasing
    FALLING = "falling"    # Temperature decreasing
    STABLE = "stable"      # Temperature stable


class DayForecast(BaseModel):
    label: str          # "Today" / "Tomorrow" / "Day 3"
    min: int
    max: int
    condition: str
    rain_percent: Optional[int] = 0
    wind: Optional[int] = 0


class WeatherAlert(BaseModel):
    """Alert for extreme weather conditions"""
    city_name: str
    level: AlertLevel
    message: str
    trigger: str  # "extreme_heat", "extreme_cold", "heavy_rain", etc.
    value: float


class TimeSeriesPoint(BaseModel):
    """Single point in a time series"""
    timestamp: str
    max_temp: int
    min_temp: int
    avg_temp: float
    condition: str
    rain_percent: Optional[int] = 0


class HistoricalStats(BaseModel):
    """Statistics for a city over a period"""
    city_name: str
    period: str  # e.g., "last_7_days", "last_30_days"
    avg_max: float
    avg_min: float
    avg_temperature: float
    max_recorded: int
    min_recorded: int
    most_common_condition: str
    rainy_days: int
    total_days: int


class TemperatureTrend(BaseModel):
    """Temperature trend analysis"""
    city_name: str
    direction: TrendDirection
    change_per_day: float  # Average change in temperature per day
    days_analyzed: int
    current_temp: int
    trend_message: str


class TrendAnalysisResponse(BaseModel):
    """Response for trend analysis"""
    city_name: str
    max_trend: TemperatureTrend
    min_trend: TemperatureTrend
    overall_pattern: str


class TimeSeriesResponse(BaseModel):
    """Response for time series data"""
    city_name: str
    data_points: List[TimeSeriesPoint]
    period: str


class HistoricalTrendsResponse(BaseModel):
    """Response for historical trends"""
    city_name: str
    current_forecast: CityForecast
    historical_stats: HistoricalStats
    trend_analysis: TrendAnalysisResponse
    recommendations: List[str] = []


class CityForecast(BaseModel):
    id: int
    name: str
    region: Optional[str] = None
    days: List[DayForecast]
    alerts: List[WeatherAlert] = []


class ForecastResponse(BaseModel):
    as_of: Optional[str] = None
    source: str = "National Meteorology Agency"
    cities: List[CityForecast]
    alerts: List[WeatherAlert] = []


class CityComparisonResponse(BaseModel):
    """Response for city comparison"""
    cities: List[CityForecast]
    hottest_city: str
    coldest_city: str
    highest_rain: str


class PaginatedForecastResponse(BaseModel):
    """Paginated forecast response"""
    total: int
    page: int
    page_size: int
    cities: List[CityForecast]
    alerts: List[WeatherAlert] = []
