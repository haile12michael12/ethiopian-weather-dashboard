"""
Time-series analysis and historical trends module.
Analyzes weather patterns over time and generates insights.
"""
from typing import List, Dict, Tuple
from statistics import mean, stdev
from .models import (
    TimeSeriesPoint, HistoricalStats, TemperatureTrend,
    TrendDirection, TrendAnalysisResponse
)


def calculate_historical_stats(records: List[Dict]) -> HistoricalStats:
    """
    Calculate historical statistics from weather records.
    
    Args:
        records: List of forecast records with MaxTemp, MinTemp, WeatherCondition, RainPercent
        
    Returns:
        HistoricalStats object with aggregated metrics
    """
    if not records:
        return None
    
    # Extract max and min temperatures
    max_temps = [r.get("MaxTempD1", 0) for r in records]
    min_temps = [r.get("MinTempD1", 0) for r in records]
    rain_percents = [r.get("RainPercentD1", 0) for r in records if r.get("RainPercentD1")]
    conditions = [r.get("WeatherConditionD1", "Unknown") for r in records]
    
    # Calculate averages
    avg_max = mean(max_temps) if max_temps else 0
    avg_min = mean(min_temps) if min_temps else 0
    avg_temperature = (avg_max + avg_min) / 2
    
    # Find extremes
    max_recorded = max(max_temps) if max_temps else 0
    min_recorded = min(min_temps) if min_temps else 0
    
    # Most common condition
    most_common_condition = max(set(conditions), key=conditions.count) if conditions else "Unknown"
    
    # Count rainy days (rain_percent > 30%)
    rainy_days = sum(1 for r in rain_percents if r > 30)
    
    city_name = records[0].get("City", "Unknown") if records else "Unknown"
    
    return HistoricalStats(
        city_name=city_name,
        period="last_7_days",
        avg_max=round(avg_max, 1),
        avg_min=round(avg_min, 1),
        avg_temperature=round(avg_temperature, 1),
        max_recorded=max_recorded,
        min_recorded=min_recorded,
        most_common_condition=most_common_condition,
        rainy_days=rainy_days,
        total_days=len(records)
    )


def analyze_temperature_trend(records: List[Dict], temp_field: str) -> TemperatureTrend:
    """
    Analyze temperature trend direction and rate of change.
    
    Args:
        records: List of forecast records sorted by date
        temp_field: Field name to analyze (e.g., "MaxTempD1", "MinTempD1")
        
    Returns:
        TemperatureTrend object with direction and rate of change
    """
    if not records or len(records) < 2:
        return None
    
    temps = [r.get(temp_field, 0) for r in records]
    
    # Calculate rate of change (linear regression simplified)
    n = len(temps)
    if n < 2:
        change_per_day = 0
        direction = TrendDirection.STABLE
    else:
        # Simple slope: (last - first) / days
        change = temps[-1] - temps[0]
        days = n - 1
        change_per_day = change / days if days > 0 else 0
        
        # Determine direction
        if change_per_day > 0.5:
            direction = TrendDirection.RISING
        elif change_per_day < -0.5:
            direction = TrendDirection.FALLING
        else:
            direction = TrendDirection.STABLE
    
    # Generate trend message
    if direction == TrendDirection.RISING:
        trend_message = f"Temperature is rising at {abs(change_per_day):.2f}°C per day"
    elif direction == TrendDirection.FALLING:
        trend_message = f"Temperature is falling at {abs(change_per_day):.2f}°C per day"
    else:
        trend_message = "Temperature is relatively stable"
    
    current_temp = temps[-1] if temps else 0
    
    return TemperatureTrend(
        city_name=records[0].get("City", "Unknown") if records else "Unknown",
        direction=direction,
        change_per_day=round(change_per_day, 2),
        days_analyzed=n,
        current_temp=current_temp,
        trend_message=trend_message
    )


def analyze_trends(records: List[Dict]) -> TrendAnalysisResponse:
    """
    Perform comprehensive trend analysis on weather data.
    
    Args:
        records: List of forecast records
        
    Returns:
        TrendAnalysisResponse with max/min trends and pattern
    """
    if not records:
        return None
    
    max_temps = [r.get("MaxTempD1", 0) for r in records]
    min_temps = [r.get("MinTempD1", 0) for r in records]
    
    max_trend = analyze_temperature_trend(records, "MaxTempD1")
    min_trend = analyze_temperature_trend(records, "MinTempD1")
    
    # Determine overall pattern
    if max_trend.direction == TrendDirection.RISING and min_trend.direction == TrendDirection.RISING:
        overall_pattern = "Warming trend: Both day and night temperatures increasing"
    elif max_trend.direction == TrendDirection.FALLING and min_trend.direction == TrendDirection.FALLING:
        overall_pattern = "Cooling trend: Both day and night temperatures decreasing"
    elif max_trend.direction == TrendDirection.RISING:
        overall_pattern = "Days getting hotter, nights stable"
    elif min_trend.direction == TrendDirection.FALLING:
        overall_pattern = "Nights getting colder, days stable"
    else:
        overall_pattern = "Stable weather pattern with minimal temperature changes"
    
    return TrendAnalysisResponse(
        city_name=records[0].get("City", "Unknown") if records else "Unknown",
        max_trend=max_trend,
        min_trend=min_trend,
        overall_pattern=overall_pattern
    )


def generate_recommendations(stats: HistoricalStats, trend_analysis: TrendAnalysisResponse) -> List[str]:
    """
    Generate weather-based recommendations based on historical data and trends.
    
    Args:
        stats: Historical statistics
        trend_analysis: Trend analysis results
        
    Returns:
        List of recommendation strings
    """
    recommendations = []
    
    # Temperature-based recommendations
    if stats.avg_max > 30:
        recommendations.append("⚠️ Hot climate: Stay hydrated and use sun protection")
    if stats.avg_max < 15:
        recommendations.append("🧥 Cool climate: Wear warm clothing layers")
    
    # Trend-based recommendations
    if trend_analysis.max_trend.direction == TrendDirection.RISING:
        if trend_analysis.max_trend.change_per_day > 2:
            recommendations.append("🌡️ Rapid heating: Expect significantly hotter conditions")
    
    if trend_analysis.min_trend.direction == TrendDirection.FALLING:
        if trend_analysis.min_trend.change_per_day < -2:
            recommendations.append("❄️ Rapid cooling at night: Prepare for cold nights")
    
    # Rain-based recommendations
    if stats.rainy_days > stats.total_days * 0.5:  # More than 50% rainy
        recommendations.append("☔ High precipitation: Carry umbrella or raincoat")
    
    if stats.most_common_condition.lower() in ["thunderstorm", "hail", "tornado"]:
        recommendations.append("⚡ Severe weather common: Check forecasts regularly")
    
    # Default recommendation
    if not recommendations:
        recommendations.append("☀️ Generally favorable weather conditions")
    
    return recommendations


def create_time_series(records: List[Dict], city_name: str) -> List[TimeSeriesPoint]:
    """
    Create time series data points from historical records.
    
    Args:
        records: List of forecast records
        city_name: Name of the city
        
    Returns:
        List of TimeSeriesPoint objects
    """
    points = []
    
    for i, record in enumerate(records):
        max_temp = record.get("MaxTempD1", 0)
        min_temp = record.get("MinTempD1", 0)
        avg_temp = (max_temp + min_temp) / 2
        condition = record.get("WeatherConditionD1", "Unknown")
        rain_percent = record.get("RainPercentD1", 0)
        
        # Use RecNum as timestamp proxy or create a sequence
        timestamp = f"Record {record.get('RecNum', i)}"
        
        point = TimeSeriesPoint(
            timestamp=timestamp,
            max_temp=max_temp,
            min_temp=min_temp,
            avg_temp=round(avg_temp, 1),
            condition=condition,
            rain_percent=rain_percent
        )
        points.append(point)
    
    return points


def compare_with_historical_average(current_max: int, current_min: int, 
                                     historical_avg_max: float, 
                                     historical_avg_min: float) -> Dict[str, str]:
    """
    Compare current forecast with historical averages.
    
    Args:
        current_max: Current day's max temperature
        current_min: Current day's min temperature
        historical_avg_max: Historical average max
        historical_avg_min: Historical average min
        
    Returns:
        Dictionary with comparison messages
    """
    comparison = {}
    
    max_diff = current_max - historical_avg_max
    min_diff = current_min - historical_avg_min
    
    if max_diff > 5:
        comparison["max"] = f"Much hotter than average (+{max_diff:.1f}°C)"
    elif max_diff > 2:
        comparison["max"] = f"Warmer than average (+{max_diff:.1f}°C)"
    elif max_diff < -5:
        comparison["max"] = f"Much cooler than average ({max_diff:.1f}°C)"
    elif max_diff < -2:
        comparison["max"] = f"Cooler than average ({max_diff:.1f}°C)"
    else:
        comparison["max"] = "Close to historical average"
    
    if min_diff > 5:
        comparison["min"] = f"Much hotter nights than average (+{min_diff:.1f}°C)"
    elif min_diff > 2:
        comparison["min"] = f"Warmer nights than average (+{min_diff:.1f}°C)"
    elif min_diff < -5:
        comparison["min"] = f"Much colder nights than average ({min_diff:.1f}°C)"
    elif min_diff < -2:
        comparison["min"] = f"Colder nights than average ({min_diff:.1f}°C)"
    else:
        comparison["min"] = "Nights close to historical average"
    
    return comparison
