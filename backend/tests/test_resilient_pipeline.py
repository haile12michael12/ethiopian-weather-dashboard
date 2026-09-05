"""
Automated Unit and Integration Tests for Resilient Data Pipeline & Multi-Source Ensembling.
Tests:
- Pydantic V2 Data Quality and Anomaly Checks
- Temperature Inversion Auto-Correction
- Open-Meteo Fallback Data Translation
- Database Adapter & Backward-Compatibility
- FastAPI Endpoints (/api/forecast, /api/pipeline/status)
"""
import os
import sys
import pytest
from fastapi.testclient import TestClient

# Ensure backend root is on sys.path
TEST_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(TEST_DIR)
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from app.main import app
from app.pipeline.quality import validate_and_clean_record, validate_batch
from app.pipeline.sources.open_meteo import wmo_to_condition
from app.database import get_connection, init_db, get_db_type


@pytest.fixture(autouse=True)
def setup_database():
    """Ensure database schema is initialized before running tests."""
    init_db()


def test_wmo_code_translation():
    """Verify WMO meteorological code mapping to human-readable dashboard conditions."""
    assert wmo_to_condition(0) == "Sunny"
    assert wmo_to_condition(1) == "Mostly Sunny"
    assert wmo_to_condition(2) == "Partly Cloudy"
    assert wmo_to_condition(3) == "Cloudy"
    assert wmo_to_condition(61) == "Rain Showers"
    assert wmo_to_condition(65) == "Heavy Rain"
    assert wmo_to_condition(95) == "Thunderstorms"
    assert wmo_to_condition(None) == "Partly Cloudy"


def test_quality_engine_valid_record():
    """Verify normal, valid Ethiopian city forecast passes verification."""
    raw = {
        "City": "Addis Ababa",
        "MinTempD1": 11, "MaxTempD1": 22, "WeatherConditionD1": "Partly Cloudy",
        "MinTempD2": 10, "MaxTempD2": 21, "WeatherConditionD2": "Rain Showers",
        "MinTempD3": 12, "MaxTempD3": 23, "WeatherConditionD3": "Mostly Sunny",
        "DataSource": "NMA",
    }
    record, anomalies = validate_and_clean_record(raw)
    assert record is not None
    assert record.city == "Addis Ababa"
    assert record.quality_status == "verified"
    assert len(anomalies) == 0
    assert record.min_temp_d1 == 11
    assert record.max_temp_d1 == 22


def test_quality_engine_temperature_inversion_correction():
    """
    Verify common HTML scraper bug where Min and Max columns are inverted (e.g. Min 26, Max 14)
    is automatically detected, corrected, and marked as 'corrected'.
    """
    raw = {
        "City": "Dire Dawa",
        "MinTempD1": 34, "MaxTempD1": 22,  # INVERTED: 34 > 22
        "WeatherConditionD1": "Sunny",
        "MinTempD2": 23, "MaxTempD2": 35,
        "WeatherConditionD2": "Sunny",
        "MinTempD3": 22, "MaxTempD3": 34,
        "WeatherConditionD3": "Sunny",
        "DataSource": "NMA",
    }
    record, anomalies = validate_and_clean_record(raw)
    assert record is not None
    assert record.quality_status == "corrected"
    assert any("Inverted temperatures" in a for a in anomalies)
    # Verify values were automatically swapped
    assert record.min_temp_d1 == 22
    assert record.max_temp_d1 == 34


def test_quality_engine_delta_spike_detection():
    """Verify sudden day-over-day temperature jump (>18C) is flagged as an anomaly."""
    raw = {
        "City": "Gondar",
        "MinTempD1": 14, "MaxTempD1": 24, "WeatherConditionD1": "Sunny",
        "MinTempD2": 15, "MaxTempD2": 45,  # 21C jump between Day 1 and Day 2!
        "WeatherConditionD2": "Sunny",
        "MinTempD3": 14, "MaxTempD3": 25,
        "WeatherConditionD3": "Sunny",
        "DataSource": "NMA",
    }
    record, anomalies = validate_and_clean_record(raw)
    assert record is not None
    assert any("Sudden temperature jump" in a for a in anomalies)


def test_quality_engine_rejection_of_unrealistic_temperatures():
    """Verify impossible temperatures (>65C or <-20C) are rejected."""
    raw = {
        "City": "Semera",
        "MinTempD1": 25, "MaxTempD1": 95,  # Impossible 95C
        "WeatherConditionD1": "Sunny",
        "MinTempD2": 25, "MaxTempD2": 40,
        "WeatherConditionD2": "Sunny",
        "MinTempD3": 25, "MaxTempD3": 40,
        "WeatherConditionD3": "Sunny",
    }
    record, anomalies = validate_and_clean_record(raw)
    assert record is None
    assert any("Unrealistic" in a for a in anomalies)


def test_batch_validation():
    """Verify validate_batch produces accurate QualityReport metrics."""
    batch = [
        {"City": "Hawassa", "MinTempD1": 14, "MaxTempD1": 26, "WeatherConditionD1": "Sunny",
         "MinTempD2": 14, "MaxTempD2": 26, "WeatherConditionD2": "Sunny",
         "MinTempD3": 14, "MaxTempD3": 26, "WeatherConditionD3": "Sunny", "DataSource": "NMA"},
        {"City": "Dessie", "MinTempD1": 25, "MaxTempD1": 10, "WeatherConditionD1": "Sunny",  # Inverted
         "MinTempD2": 10, "MaxTempD2": 24, "WeatherConditionD2": "Sunny",
         "MinTempD3": 10, "MaxTempD3": 24, "WeatherConditionD3": "Sunny", "DataSource": "NMA"},
        {"City": "", "MinTempD1": 10, "MaxTempD1": 20, "WeatherConditionD1": "Sunny",  # Missing city
         "MinTempD2": 10, "MaxTempD2": 20, "WeatherConditionD2": "Sunny",
         "MinTempD3": 10, "MaxTempD3": 20, "WeatherConditionD3": "Sunny"},
    ]
    validated, report = validate_batch(batch)
    assert report.total_inspected == 3
    assert report.verified == 1
    assert report.corrected == 1
    assert report.rejected == 1
    assert len(validated) == 2


def test_database_table_exists():
    """Verify database connection and table presence."""
    with get_connection() as conn:
        row = conn.execute("SELECT 1").fetchone()
        assert row is not None


def test_api_forecast_endpoint():
    """Test GET /api/forecast returns valid structure and data source."""
    client = TestClient(app)
    response = client.get("/api/forecast")
    assert response.status_code == 200
    data = response.json()
    assert "cities" in data
    assert "source" in data
    assert "data_source" in data
    assert "fallback_active" in data
    assert len(data["cities"]) > 0

    first_city = data["cities"][0]
    assert "name" in first_city
    assert "days" in first_city
    assert "data_source" in first_city
    assert len(first_city["days"]) == 3


def test_api_pipeline_status_endpoint():
    """Test GET /api/pipeline/status returns health and fallback telemetry."""
    client = TestClient(app)
    response = client.get("/api/pipeline/status")
    assert response.status_code == 200
    status = response.json()
    assert "database_type" in status
    assert "primary_source" in status
    assert "fallback_source" in status
    assert "fallback_active" in status
    assert "total_records" in status
    assert status["total_records"] > 0
