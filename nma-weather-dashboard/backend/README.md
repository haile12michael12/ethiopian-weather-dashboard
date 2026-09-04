# NMA Weather API

FastAPI service that reads the SQLite table the `NMA_web_Scrapping.py`
Airflow DAG writes (`NMAthreedaysForcasetData`) and exposes it as JSON for
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
export DB_PATH=./NMA_Threedays_forcast_DataBase.db
uvicorn app.main:app --reload --port 8000
```

## Endpoints

- `GET /api/health` — liveness check
- `GET /api/forecast` — latest 3-day forecast for every city
- `GET /api/forecast/{city_name}` — latest forecast for one city
