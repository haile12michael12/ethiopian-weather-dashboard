"""
Resilient Weather Pipeline Orchestrator.
Executes the multi-source ingestion lifecycle:
1. Primary NMA scrape attempt with retries
2. Secondary Open-Meteo fallback on failure or city omissions
3. Pydantic V2 data validation and anomaly correction
4. Persistence to PostgreSQL/TimescaleDB or SQLite
5. Quality and source lineage reporting
"""
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

from .cities import ETHIOPIAN_CITIES
from .sources.nma import fetch_nma_forecast, NMAScraperError
from .sources.open_meteo import fetch_all_cities_open_meteo, fetch_city_forecast_open_meteo
from .quality import validate_batch, ValidatedForecastRecord
from ..database import get_connection, init_db, is_postgres

logger = logging.getLogger(__name__)


class PipelineMetrics(BaseModel):
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    success: bool = True
    database_type: str = "SQLite"
    primary_source_status: str = "operational"  # "operational", "failed", "partially_degraded"
    fallback_active: bool = False
    total_ingested: int = 0
    nma_count: int = 0
    open_meteo_count: int = 0
    corrected_anomalies: int = 0
    rejected_count: int = 0
    cities_updated: List[str] = Field(default_factory=list)


def run_resilient_ingest() -> PipelineMetrics:
    """
    Executes the end-to-end resilient ingestion pipeline.
    """
    init_db()
    metrics = PipelineMetrics(database_type="PostgreSQL / TimescaleDB" if is_postgres() else "SQLite")

    raw_records: List[Dict[str, Any]] = []
    nma_cities_found = set()

    # Step 1: Attempt Primary Scraper (NMA)
    try:
        logger.info("Attempting primary ingest from National Meteorology Agency (NMA)...")
        nma_records = fetch_nma_forecast(max_retries=2, retry_delay=1.0)
        raw_records.extend(nma_records)
        nma_cities_found = {r["City"] for r in nma_records}
        metrics.primary_source_status = "operational"
        logger.info(f"NMA primary ingest retrieved {len(nma_records)} cities.")
    except (NMAScraperError, Exception) as exc:
        logger.warning(f"Primary NMA ingest unavailable ({exc}). Engaging secondary fallback.")
        metrics.primary_source_status = f"offline: {exc}"
        metrics.fallback_active = True

    # Step 2: Determine Missing Cities & Query Fallback (Open-Meteo)
    all_target_cities = set(ETHIOPIAN_CITIES.keys())
    missing_cities = all_target_cities - nma_cities_found

    if missing_cities:
        logger.info(f"Querying Open-Meteo fallback for {len(missing_cities)} cities: {sorted(list(missing_cities))}")
        fallback_records = fetch_all_cities_open_meteo(cities=list(missing_cities))
        raw_records.extend(fallback_records)
        metrics.fallback_active = True

    # Step 3: Run Data Quality and Anomaly Validation
    logger.info(f"Validating {len(raw_records)} total records through Data Quality Engine...")
    validated_records, quality_report = validate_batch(raw_records)

    metrics.corrected_anomalies = quality_report.corrected
    metrics.rejected_count = quality_report.rejected

    # Step 4: Persist Validated Records to Database
    if not validated_records:
        logger.error("No valid forecast records to persist.")
        metrics.success = False
        return metrics

    with get_connection() as conn:
        for r in validated_records:
            d = r.to_dict()
            if d["DataSource"] == "NMA":
                metrics.nma_count += 1
            else:
                metrics.open_meteo_count += 1

            metrics.cities_updated.append(d["City"])

            # Insert into weather_forecasts
            conn.execute(
                """
                INSERT INTO weather_forecasts (
                    City, MinTempD1, MaxTempD1, WeatherConditionD1, RainPercentD1, WindD1,
                    MinTempD2, MaxTempD2, WeatherConditionD2, RainPercentD2, WindD2,
                    MinTempD3, MaxTempD3, WeatherConditionD3, RainPercentD3, WindD3,
                    DataSource, QualityStatus
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    d["City"], d["MinTempD1"], d["MaxTempD1"], d["WeatherConditionD1"], d["RainPercentD1"], d["WindD1"],
                    d["MinTempD2"], d["MaxTempD2"], d["WeatherConditionD2"], d["RainPercentD2"], d["WindD2"],
                    d["MinTempD3"], d["MaxTempD3"], d["WeatherConditionD3"], d["RainPercentD3"], d["WindD3"],
                    d["DataSource"], d["QualityStatus"]
                )
            )

            # Also maintain NMAthreedaysForcasetData table for legacy queries if not using views
            if not is_postgres():
                conn.execute(
                    """
                    INSERT INTO NMAthreedaysForcasetData (
                        City, MinTempD1, MaxTempD1, WeatherConditionD1, RainPercentD1, WindD1,
                        MinTempD2, MaxTempD2, WeatherConditionD2, RainPercentD2, WindD2,
                        MinTempD3, MaxTempD3, WeatherConditionD3, RainPercentD3, WindD3,
                        DataSource, QualityStatus
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        d["City"], d["MinTempD1"], d["MaxTempD1"], d["WeatherConditionD1"], d["RainPercentD1"], d["WindD1"],
                        d["MinTempD2"], d["MaxTempD2"], d["WeatherConditionD2"], d["RainPercentD2"], d["WindD2"],
                        d["MinTempD3"], d["MaxTempD3"], d["WeatherConditionD3"], d["RainPercentD3"], d["WindD3"],
                        d["DataSource"], d["QualityStatus"]
                    )
                )

        conn.commit()

    metrics.total_ingested = len(validated_records)
    logger.info(
        f"Pipeline ingest complete. Total: {metrics.total_ingested} "
        f"(NMA: {metrics.nma_count}, Open-Meteo: {metrics.open_meteo_count}, "
        f"Corrected: {metrics.corrected_anomalies})"
    )

    return metrics
