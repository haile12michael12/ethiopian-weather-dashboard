from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from ..database import get_connection, table_exists
from ..models import (
    ForecastResponse, CityForecast, DayForecast, 
    CityComparisonResponse, PaginatedForecastResponse,
    TimeSeriesResponse, HistoricalTrendsResponse
)
from ..alerts import detect_alerts, detect_all_alerts
from ..timeseries import (
    calculate_historical_stats, analyze_trends, generate_recommendations,
    create_time_series, compare_with_historical_average
)
from ..regions import region_for

router = APIRouter(prefix="/api", tags=["forecast"])

DAY_LABELS = ["Today", "Tomorrow", "Day 3"]


def _build_day_forecast(row: dict, day_num: int) -> DayForecast:
    """Helper to build DayForecast from row data"""
    return DayForecast(
        label=DAY_LABELS[day_num - 1],
        min=row[f"MinTempD{day_num}"],
        max=row[f"MaxTempD{day_num}"],
        condition=row[f"WeatherConditionD{day_num}"],
        rain_percent=row.get(f"RainPercentD{day_num}", 0),
        wind=row.get(f"WindD{day_num}", 0)
    )


def _build_city_forecast(row: dict) -> CityForecast:
    """Helper to build CityForecast from row data"""
    days = [_build_day_forecast(row, i) for i in range(1, 4)]
    city = CityForecast(
        id=row["RecNum"],
        name=row["City"],
        region=region_for(row["City"]),
        days=days
    )
    # Attach alerts to the city
    city.alerts = detect_alerts(city)
    return city


@router.get("/forecast", response_model=ForecastResponse)
def get_forecast():
    """
    Returns the most recent forecast row per city with alerts.
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

    cities = [_build_city_forecast(dict(row)) for row in rows]
    all_alerts = detect_all_alerts(cities)

    return ForecastResponse(cities=cities, alerts=all_alerts)


@router.get("/forecast/{city_name}", response_model=CityForecast)
def get_city_forecast(city_name: str):
    """Get forecast for a specific city"""
    if not table_exists():
        raise HTTPException(status_code=503, detail="Forecast table not found")

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

    return _build_city_forecast(dict(row))


@router.get("/alerts", response_model=List)
def get_alerts(
    level: Optional[str] = Query(None, description="Filter by alert level: info, warning, critical"),
    city: Optional[str] = Query(None, description="Filter by city name")
):
    """
    Get all active weather alerts.
    
    Query Parameters:
    - level: Filter by severity (info, warning, critical)
    - city: Filter by city name
    """
    if not table_exists():
        raise HTTPException(status_code=503, detail="Forecast table not found")

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

    cities = [_build_city_forecast(dict(row)) for row in rows]
    all_alerts = detect_all_alerts(cities)
    
    # Apply filters
    if level:
        all_alerts = [a for a in all_alerts if a.level == level]
    if city:
        all_alerts = [a for a in all_alerts if a.city_name.lower() == city.lower()]
    
    return all_alerts


@router.get("/compare", response_model=CityComparisonResponse)
def compare_cities(
    cities: str = Query(..., description="Comma-separated list of city names")
):
    """
    Compare weather across multiple cities.
    
    Example: /api/compare?cities=Addis Ababa,Dire Dawa,Hawassa
    """
    if not table_exists():
        raise HTTPException(status_code=503, detail="Forecast table not found")

    city_names = [c.strip() for c in cities.split(",")]
    
    if len(city_names) < 2:
        raise HTTPException(status_code=400, detail="Provide at least 2 cities to compare")
    
    if len(city_names) > 10:
        raise HTTPException(status_code=400, detail="Maximum 10 cities allowed for comparison")

    with get_connection() as conn:
        placeholders = ",".join("?" * len(city_names))
        rows = conn.execute(
            f"""
            SELECT t.*
            FROM NMAthreedaysForcasetData t
            INNER JOIN (
                SELECT City, MAX(RecNum) AS max_rec
                FROM NMAthreedaysForcasetData
                WHERE City IN ({placeholders})
                GROUP BY City
            ) latest
            ON t.City = latest.City AND t.RecNum = latest.max_rec
            ORDER BY t.City ASC
            """,
            city_names,
        ).fetchall()

    if not rows:
        raise HTTPException(status_code=404, detail="No forecast found for the given cities")

    cities_data = [_build_city_forecast(dict(row)) for row in rows]
    
    # Calculate comparison metrics
    max_temps = [c.days[0].max for c in cities_data]
    min_temps = [c.days[0].min for c in cities_data]
    rain_percents = [c.days[0].rain_percent or 0 for c in cities_data]
    
    hottest_idx = max_temps.index(max(max_temps))
    coldest_idx = min_temps.index(min(min_temps))
    highest_rain_idx = rain_percents.index(max(rain_percents))
    
    return CityComparisonResponse(
        cities=cities_data,
        hottest_city=cities_data[hottest_idx].name,
        coldest_city=cities_data[coldest_idx].name,
        highest_rain=cities_data[highest_rain_idx].name
    )


@router.get("/forecast-advanced", response_model=PaginatedForecastResponse)
def get_forecast_advanced(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    region: Optional[str] = Query(None, description="Filter by region"),
    sort_by: str = Query("name", description="Sort by: name, hottest, coldest, highest_rain"),
    condition: Optional[str] = Query(None, description="Filter by weather condition")
):
    """
    Advanced forecast retrieval with filtering, sorting, and pagination.
    
    Query Parameters:
    - page: Page number (default 1)
    - page_size: Number of results per page (1-100, default 10)
    - region: Filter by region name
    - sort_by: Sort order (name, hottest, coldest, highest_rain)
    - condition: Filter by weather condition
    """
    if not table_exists():
        raise HTTPException(status_code=503, detail="Forecast table not found")

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

    cities = [_build_city_forecast(dict(row)) for row in rows]
    
    # Apply filters
    if region:
        cities = [c for c in cities if c.region and c.region.lower() == region.lower()]
    
    if condition:
        cities = [c for c in cities if condition.lower() in c.days[0].condition.lower()]
    
    # Apply sorting
    if sort_by == "hottest":
        cities.sort(key=lambda c: c.days[0].max, reverse=True)
    elif sort_by == "coldest":
        cities.sort(key=lambda c: c.days[0].min)
    elif sort_by == "highest_rain":
        cities.sort(key=lambda c: c.days[0].rain_percent or 0, reverse=True)
    else:  # name
        cities.sort(key=lambda c: c.name)
    
    # Apply pagination
    total = len(cities)
    start = (page - 1) * page_size
    end = start + page_size
    paginated_cities = cities[start:end]
    
    all_alerts = detect_all_alerts(paginated_cities)
    
    return PaginatedForecastResponse(
        total=total,
        page=page,
        page_size=page_size,
        cities=paginated_cities,
        alerts=all_alerts
    )


@router.get("/timeseries/{city_name}", response_model=TimeSeriesResponse)
def get_time_series(
    city_name: str,
    days: int = Query(7, ge=1, le=90, description="Number of days to retrieve (1-90)")
):
    """
    Get historical time series data for a city.
    
    Query Parameters:
    - days: Number of historical records to retrieve (max 90)
    
    Returns time series data showing temperature trends and patterns.
    """
    if not table_exists():
        raise HTTPException(status_code=503, detail="Forecast table not found")

    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT * FROM NMAthreedaysForcasetData
            WHERE City = ?
            ORDER BY RecNum DESC
            LIMIT ?
            """,
            (city_name, days),
        ).fetchall()

    if not rows:
        raise HTTPException(status_code=404, detail=f"No forecast found for '{city_name}'")

    # Convert to dicts and reverse to show in chronological order
    records = [dict(row) for row in reversed(rows)]
    
    # Create time series points
    time_series_data = create_time_series(records, city_name)
    
    return TimeSeriesResponse(
        city_name=city_name,
        data_points=time_series_data,
        period=f"last_{len(records)}_days"
    )


@router.get("/trends/{city_name}")
def get_city_trends(city_name: str):
    """
    Get temperature trend analysis for a city.
    
    Returns:
    - Trend direction (rising, falling, stable) for max and min temps
    - Rate of change per day
    - Overall weather pattern
    """
    if not table_exists():
        raise HTTPException(status_code=503, detail="Forecast table not found")

    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT * FROM NMAthreedaysForcasetData
            WHERE City = ?
            ORDER BY RecNum DESC
            LIMIT 30
            """,
            (city_name,),
        ).fetchall()

    if not rows:
        raise HTTPException(status_code=404, detail=f"No forecast found for '{city_name}'")

    records = [dict(row) for row in reversed(rows)]
    trend_analysis = analyze_trends(records)
    
    return trend_analysis


@router.get("/historical/{city_name}", response_model=HistoricalTrendsResponse)
def get_historical_trends(
    city_name: str,
    period_days: int = Query(30, ge=7, le=180, description="Analysis period in days (7-180)")
):
    """
    Get comprehensive historical analysis and trends for a city.
    
    Includes:
    - Current forecast
    - Historical statistics (avg, max, min temps)
    - Trend analysis (rising/falling patterns)
    - Weather recommendations
    
    Query Parameters:
    - period_days: Number of days to analyze (7-180, default 30)
    """
    if not table_exists():
        raise HTTPException(status_code=503, detail="Forecast table not found")

    with get_connection() as conn:
        # Get current forecast
        current = conn.execute(
            """
            SELECT * FROM NMAthreedaysForcasetData
            WHERE City = ?
            ORDER BY RecNum DESC
            LIMIT 1
            """,
            (city_name,),
        ).fetchone()

        # Get historical data
        historical = conn.execute(
            """
            SELECT * FROM NMAthreedaysForcasetData
            WHERE City = ?
            ORDER BY RecNum DESC
            LIMIT ?
            """,
            (city_name, period_days),
        ).fetchall()

    if not current or not historical:
        raise HTTPException(status_code=404, detail=f"No forecast found for '{city_name}'")

    # Build current forecast
    current_dict = dict(current)
    current_forecast = _build_city_forecast(current_dict)
    
    # Calculate statistics
    historical_records = [dict(row) for row in reversed(historical)]
    historical_stats = calculate_historical_stats(historical_records)
    
    # Analyze trends
    trend_analysis = analyze_trends(historical_records)
    
    # Generate recommendations
    recommendations = generate_recommendations(historical_stats, trend_analysis)
    
    return HistoricalTrendsResponse(
        city_name=city_name,
        current_forecast=current_forecast,
        historical_stats=historical_stats,
        trend_analysis=trend_analysis,
        recommendations=recommendations
    )


@router.get("/statistics/{city_name}")
def get_city_statistics(
    period_days: int = Query(30, ge=7, le=180, description="Analysis period in days")
):
    """
    Get statistical summary of weather for a city.
    
    Returns averages, extremes, and frequency of conditions over the specified period.
    """
    if not table_exists():
        raise HTTPException(status_code=503, detail="Forecast table not found")

    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT * FROM NMAthreedaysForcasetData
            WHERE City = ?
            ORDER BY RecNum DESC
            LIMIT ?
            """,
            (city_name, period_days),
        ).fetchall()

    if not rows:
        raise HTTPException(status_code=404, detail=f"No forecast found for '{city_name}'")

    records = [dict(row) for row in rows]
    stats = calculate_historical_stats(records)
    
    return stats
