# Weather API

FastAPI service that reads the SQLite table the `web_scrapping.py`
Airflow DAG writes (`threedaysForcasetData`) and exposes it as JSON for
the React dashboard.

## Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Run against a live Airflow DB

```bash
export DB_PATH=~/airflow/harvestedfiles/NMA_Threedays_forcast_DataBase.db
uvicorn app.main:app --reload --port 8000
```

## Run with sample data (no Airflow needed)

```bash
python seed_db.py
export DB_PATH=./Threedays_forcast_DataBase.db
uvicorn app.main:app --reload --port 8000
```

## Resilient Data Pipeline & Multi-Source Ensembling

The backend includes a resilient weather ingestion pipeline that protects against government portal downtime:
1. **Primary Ingestion**: Scrapes Ethiopia's National Meteorology Agency (`ethiomet.gov.et`).
2. **Data Quality & Anomaly Engine**: Enforces meteorological constraints using Pydantic V2, auto-correcting inverted temperature columns and detecting delta spikes.
3. **Secondary Fallback Ingestion**: Automatically engages the Open-Meteo ECMWF/GFS global API for Ethiopian cities if the NMA portal 404s, times out, or omits cities.
4. **TimescaleDB / PostgreSQL Support**: Connects to TimescaleDB with automated hypertables, or falls back to local SQLite.

### Running the Resilient Pipeline (On-Demand)

You can trigger a fresh harvest and quality-checked ingestion without running Apache Airflow:

```bash
python run_pipeline.py
```

### PostgreSQL / TimescaleDB Migration

To migrate existing SQLite records to a TimescaleDB instance:

```bash
python migrate_to_timescaledb.py --sqlite-path ./Threedays_forcast_DataBase.db --target-url postgresql://postgres:secret@localhost:5432/weather_db
```

Set `DATABASE_URL` to point the FastAPI backend to TimescaleDB:

```bash
export DATABASE_URL=postgresql://postgres:secret@localhost:5432/weather_db
uvicorn app.main:app --reload --port 8000
```

## Endpoints

- `GET /api/health` — liveness check
- `GET /api/forecast` — latest 3-day forecast for every city
- `GET /api/forecast` — latest 3-day forecast for every city (includes data lineage & fallback status)
- `GET /api/forecast/{city_name}` — latest forecast for one city
- `GET /api/pipeline/status` — telemetry on active data source (NMA vs Open-Meteo), database engine, and quality metrics
- `GET /api/alerts` — active extreme heat, cold, and storm alerts
- `GET /api/compare?cities=Addis Ababa,Hawassa` — compare metrics across multiple cities
- `GET /api/timeseries/{city_name}` — historical observations and trends
- `GET /api/historical/{city_name}` — statistical summaries and climate recommendations
