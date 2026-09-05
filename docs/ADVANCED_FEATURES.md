# Backend Advanced Features Documentation

## New Endpoints

### 1. **Weather Alerts** - `/api/alerts`
Retrieve all active weather alerts with automatic detection of extreme conditions.

```bash
# Get all alerts
GET /api/alerts

# Filter by severity level
GET /api/alerts?level=critical
GET /api/alerts?level=warning
GET /api/alerts?level=info

# Filter by city
GET /api/alerts?city=Addis Ababa

# Combine filters
GET /api/alerts?level=critical&city=Dire Dawa
```

**Alert Types:**
- `extreme_heat`: Temperature ≥ 35°C (Critical if ≥ 40°C)
- `extreme_cold`: Temperature ≤ 5°C
- `heavy_rain`: Rain probability ≥ 60% (Critical if ≥ 80%)
- `hazardous_condition`: Thunderstorm, hail, tornado detected

**Response Example:**
```json
[
  {
    "city_name": "Addis Ababa",
    "level": "critical",
    "message": "Extreme heat warning: Temperature expected to reach 38°C",
    "trigger": "extreme_heat",
    "value": 38.0
  }
]
```

---

### 2. **City Comparison** - `/api/compare`
Compare weather conditions across multiple cities.

```bash
# Compare 2+ cities (max 10)
GET /api/compare?cities=Addis Ababa,Dire Dawa,Hawassa

# Multiple words in city names
GET /api/compare?cities=Addis%20Ababa,Dire%20Dawa
```

**Response Example:**
```json
{
  "cities": [
    {
      "id": 1,
      "name": "Addis Ababa",
      "region": "Addis Ababa",
      "days": [...],
      "alerts": []
    },
    {...}
  ],
  "hottest_city": "Dire Dawa",
  "coldest_city": "Hawassa",
  "highest_rain": "Addis Ababa"
}
```

---

### 3. **Advanced Filtering & Pagination** - `/api/forecast-advanced`
Retrieve forecasts with advanced filtering, sorting, and pagination.

```bash
# Get page 1 with 10 items
GET /api/forecast-advanced

# Custom pagination
GET /api/forecast-advanced?page=2&page_size=20

# Filter by region
GET /api/forecast-advanced?region=Oromia

# Filter by weather condition
GET /api/forecast-advanced?condition=rainy

# Sort options: name, hottest, coldest, highest_rain
GET /api/forecast-advanced?sort_by=hottest

# Combine multiple filters
GET /api/forecast-advanced?page=1&page_size=15&region=Amhara&sort_by=coldest
```

**Response Example:**
```json
{
  "total": 47,
  "page": 1,
  "page_size": 10,
  "cities": [...],
  "alerts": [...]
}
```

---

## Alert Detection Thresholds

| Condition | Threshold | Alert Level |
|-----------|-----------|-------------|
| Extreme Heat | ≥ 35°C | WARNING |
| Extreme Heat | ≥ 40°C | CRITICAL |
| Extreme Cold | ≤ 5°C | WARNING |
| Heavy Rain | ≥ 60% | INFO |
| Heavy Rain | ≥ 80% | WARNING |
| Hazardous Conditions | Detected | CRITICAL |

---

## Integration with Frontend

### Load Alerts on App Start
```javascript
const response = await fetch('/api/forecast');
const data = await response.json();
const alerts = data.alerts; // Already included in response
```

### Get Alerts for Specific Level
```javascript
const response = await fetch('/api/alerts?level=critical');
const criticalAlerts = await response.json();
```

### Compare Multiple Cities
```javascript
const response = await fetch('/api/compare?cities=Addis Ababa,Dire Dawa');
const comparison = await response.json();
// Use hottest_city, coldest_city, highest_rain fields
```

### Advanced Search with Pagination
```javascript
const response = await fetch(
  '/api/forecast-advanced?page=1&page_size=15&region=Oromia&sort_by=hottest'
);
const paginated = await response.json();
// Handle pagination: total, page, page_size
```

---

## Database Fields Used

The backend automatically extracts these fields (if available):
- `RainPercentD1`, `RainPercentD2`, `RainPercentD3` - Rain probability
- `WindD1`, `WindD2`, `WindD3` - Wind speed
- Extended condition strings with keywords: thunderstorm, heavy rain, hail, tornado

**Note:** If these fields don't exist in your database, they default to 0. Update the scraper to collect additional data as needed.

---

## Error Responses

```json
{
  "detail": "Forecast table not found yet — has the NMA scraper DAG run at least once?"
}
```

Common errors:
- **503**: Database not initialized
- **404**: City not found in forecast data
- **400**: Invalid query parameters (e.g., less than 2 cities for comparison)

---

## 4. **Time Series Analysis** - `/api/timeseries/{city_name}`
Retrieve historical time series data to visualize weather trends over time.

```bash
# Get 7 days of historical data (default)
GET /api/timeseries/Addis Ababa

# Get 30 days of history
GET /api/timeseries/Dire Dawa?days=30

# Maximum 90 days
GET /api/timeseries/Hawassa?days=90
```

**Response Example:**
```json
{
  "city_name": "Addis Ababa",
  "period": "last_7_days",
  "data_points": [
    {
      "timestamp": "Record 100",
      "max_temp": 28,
      "min_temp": 15,
      "avg_temp": 21.5,
      "condition": "Partly Cloudy",
      "rain_percent": 20
    },
    {...}
  ]
}
```

**Use Cases:**
- Chart temperature trends over time
- Identify warming/cooling patterns
- Visualize precipitation cycles
- Detect anomalies in weather conditions

---

## 5. **Temperature Trend Analysis** - `/api/trends/{city_name}`
Get detailed trend analysis showing temperature direction and rate of change.

```bash
GET /api/trends/Addis Ababa
```

**Response Example:**
```json
{
  "city_name": "Addis Ababa",
  "max_trend": {
    "city_name": "Addis Ababa",
    "direction": "rising",
    "change_per_day": 0.82,
    "days_analyzed": 30,
    "current_temp": 28,
    "trend_message": "Temperature is rising at 0.82°C per day"
  },
  "min_trend": {
    "city_name": "Addis Ababa",
    "direction": "stable",
    "change_per_day": 0.15,
    "days_analyzed": 30,
    "current_temp": 15,
    "trend_message": "Temperature is relatively stable"
  },
  "overall_pattern": "Warming trend: Both day and night temperatures increasing"
}
```

**Trend Directions:**
- `rising`: Temperature increasing (> 0.5°C per day)
- `falling`: Temperature decreasing (< -0.5°C per day)
- `stable`: Temperature relatively constant

---

## 6. **Historical Trends & Recommendations** - `/api/historical/{city_name}`
Comprehensive historical analysis with AI-generated recommendations.

```bash
# Analyze last 30 days (default)
GET /api/historical/Addis Ababa

# Analyze last 90 days
GET /api/historical/Dire Dawa?period_days=90

# Maximum 180 days
GET /api/historical/Hawassa?period_days=180
```

**Response Example:**
```json
{
  "city_name": "Addis Ababa",
  "current_forecast": {...},
  "historical_stats": {
    "city_name": "Addis Ababa",
    "period": "last_7_days",
    "avg_max": 28.5,
    "avg_min": 15.2,
    "avg_temperature": 21.85,
    "max_recorded": 32,
    "min_recorded": 12,
    "most_common_condition": "Partly Cloudy",
    "rainy_days": 2,
    "total_days": 7
  },
  "trend_analysis": {...},
  "recommendations": [
    "☀️ Generally favorable weather conditions",
    "⚠️ Hot climate: Stay hydrated and use sun protection",
    "☔ High precipitation: Carry umbrella or raincoat"
  ]
}
```

**Recommendation Types:**
- 🌡️ Temperature alerts and guidance
- 📈 Trend-based warnings (rapid heating/cooling)
- ☔ Precipitation preparation
- ⚡ Severe weather alerts
- 🧥 Clothing suggestions

---

## 7. **Weather Statistics** - `/api/statistics/{city_name}`
Get aggregated statistics for a city over a specified period.

```bash
# Get 30-day statistics (default)
GET /api/statistics/Addis Ababa

# Get 90-day statistics
GET /api/statistics/Dire Dawa?period_days=90
```

**Response Example:**
```json
{
  "city_name": "Addis Ababa",
  "period": "last_30_days",
  "avg_max": 27.8,
  "avg_min": 14.9,
  "avg_temperature": 21.35,
  "max_recorded": 33,
  "min_recorded": 10,
  "most_common_condition": "Partly Cloudy",
  "rainy_days": 8,
  "total_days": 30
}
```

---

## Time-Series Analysis Features

### Trend Detection
- **Rising**: Temperature increasing > 0.5°C per day
- **Falling**: Temperature decreasing < -0.5°C per day
- **Stable**: Temperature relatively unchanged

### Pattern Recognition
- Warming trends: Both day and night temperatures rising
- Cooling trends: Both day and night temperatures falling
- Night-specific trends: Only night temperatures changing
- Day-specific trends: Only day temperatures changing

### Recommendations Generated
The system automatically generates recommendations based on:
1. **Temperature extremes** - Heat/cold warnings
2. **Trend direction** - Rapid changes ahead
3. **Precipitation patterns** - Rain preparation
4. **Severe conditions** - Thunderstorms, hail, etc.
5. **Historical averages** - Comparison with norm

---

## Frontend Integration Examples

### Display Temperature Trends
```javascript
// Get 30-day trend data
const response = await fetch('/api/timeseries/Addis Ababa?days=30');
const timeSeries = await response.json();

// Plot data points using Recharts
timeSeries.data_points.forEach(point => {
  // Add to chart: timestamp, max_temp, min_temp
});
```

### Show Current Trends
```javascript
const response = await fetch('/api/trends/Addis Ababa');
const trends = await response.json();

// Display trend direction and message
console.log(trends.max_trend.trend_message);  // "Temperature is rising at 0.82°C per day"
console.log(trends.overall_pattern);          // "Warming trend: Both day and night..."
```

### Display Historical Recommendations
```javascript
const response = await fetch('/api/historical/Addis Ababa?period_days=30');
const historical = await response.json();

// Show recommendations to user
historical.recommendations.forEach(rec => {
  console.log(rec);  // "☀️ Generally favorable weather conditions"
});
```

---

## Performance & Caching

- **Time Series**: Limited to 90 days (database query performance)
- **Historical Analysis**: Limited to 180 days
- **Database Queries**: Optimized with indexes on City and RecNum
- **Pagination**: Reduces memory usage for large datasets

---

## Data Quality Notes

- All calculations use Day 1 forecast data by default
- Rain percentages default to 0 if not available
- Wind speeds default to 0 if not available
- Trend analysis requires at least 2 data points
- Recommendations update based on latest data
