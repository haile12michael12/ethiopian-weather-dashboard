from fastapi import APIRouter, HTTPException
from ..database import get_connection, table_exists
from ..models import ForecastResponse, CityForecast, DayForecast
from ..regions import region_for

router = APIRouter(prefix="/api", tags=["forecast"])

DAY_LABELS = ["Today", "Tomorrow", "Day 3"]


@router.get("/forecast", response_model=ForecastResponse)
def get_forecast():
    """
    Returns the most recent forecast row per city, reshaped into the
    {city, days:[{min,max,condition}]} form the frontend consumes.

    The scraper inserts one new row per city every DAG run, so "most
    recent" is the row with the highest RecNum for that city.
    """
    if not table_exists():
        raise HTTPException(
            status_code=503,
            detail="Forecast table not found yet — has the NMA scraper DAG run at least once?",
        )

    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT t.*
            FROM NMAthreedaysForcasetData t
            INNER JOIN (
                SELECT City, MAX(RecNum) AS max_rec
                FROM NMAthreedaysForcasetData
                GROUP BY City
            ) latest
            ON t.City = latest.City AND t.RecNum = latest.max_rec
            ORDER BY t.City ASC
            """
        ).fetchall()

    cities = []
    for row in rows:
        days = [
            DayForecast(label=DAY_LABELS[0], min=row["MinTempD1"], max=row["MaxTempD1"], condition=row["WeatherConditionD1"]),
            DayForecast(label=DAY_LABELS[1], min=row["MinTempD2"], max=row["MaxTempD2"], condition=row["WeatherConditionD2"]),
            DayForecast(label=DAY_LABELS[2], min=row["MinTempD3"], max=row["MaxTempD3"], condition=row["WeatherConditionD3"]),
        ]
        cities.append(
            CityForecast(id=row["RecNum"], name=row["City"], region=region_for(row["City"]), days=days)
        )

    return ForecastResponse(cities=cities)


@router.get("/forecast/{city_name}", response_model=CityForecast)
def get_city_forecast(city_name: str):
    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT * FROM NMAthreedaysForcasetData
            WHERE City = ?
            ORDER BY RecNum DESC LIMIT 1
            """,
            (city_name,),
        ).fetchone()

    if row is None:
        raise HTTPException(status_code=404, detail=f"No forecast found for '{city_name}'")

    days = [
        DayForecast(label=DAY_LABELS[0], min=row["MinTempD1"], max=row["MaxTempD1"], condition=row["WeatherConditionD1"]),
        DayForecast(label=DAY_LABELS[1], min=row["MinTempD2"], max=row["MaxTempD2"], condition=row["WeatherConditionD2"]),
        DayForecast(label=DAY_LABELS[2], min=row["MinTempD3"], max=row["MaxTempD3"], condition=row["WeatherConditionD3"]),
    ]
    return CityForecast(id=row["RecNum"], name=row["City"], region=region_for(row["City"]), days=days)
