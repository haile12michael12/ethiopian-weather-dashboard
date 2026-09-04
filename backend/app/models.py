from typing import List, Optional
from pydantic import BaseModel


class DayForecast(BaseModel):
    label: str          # "Today" / "Tomorrow" / "Day 3"
    min: int
    max: int
    condition: str


class CityForecast(BaseModel):
    id: int
    name: str
    region: Optional[str] = None
    days: List[DayForecast]


class ForecastResponse(BaseModel):
    as_of: Optional[str] = None
    source: str = "National Meteorology Agency"
    cities: List[CityForecast]
