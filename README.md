# ethiopian Weather Dashboard

Full-stack project built around the existing Airflow scraper
(`ingestion/airflow/Scrapping.py`), which pulls Ethiopia's National
Meteorology Agency three-day forecast into a SQLite table
(`NMAthreedaysForcasetData`) once a day.

```
ethiopian-weather-dashboard/
├── ingestion/
│   └── airflow/
│       └── Scrapping.py       # Airflow ingestion job
├── backend/                   # FastAPI service and data pipeline
│   ├── app/
│   │   ├── main.py
│   │   ├── database.py
│   │   ├── models.py
│   │   ├── regions.py
│   │   ├── agro.py
│   │   ├── alerts.py
│   │   ├── timeseries.py
│   │   ├── pipeline/
│   │   ├── notifications/
│   │   └── routes/
│   ├── tests/
│   ├── seed_db.py
│   ├── run_pipeline.py
│   ├── run_telegram_bot.py
│   ├── requirements.txt
│   └── README.md
├── frontend/                  # React + Vite dashboard
│   ├── src/
│   │   ├── App.jsx
│   │   ├── theme.js
│   │   ├── api/
│   │   ├── data/
│   │   ├── hooks/
│   │   ├── utils/
│   │   └── components/
│   ├── public/sw.js
│   ├── package.json
│   └── README.md
├── docker-compose.yml
├── docs/
└── README.md
```

## How the pieces connect

1. **Airflow ingestion job** (`ingestion/airflow/Scrapping.py`) runs daily, scrapes
   ethiomet.gov.et, and appends a row per city to
   `~/airflow/harvestedfiles/NMA_Threedays_forcast_DataBase.db`.
2. **Backend** (`backend/`) is a small FastAPI service that reads the
   *latest* row per city from that same SQLite file and serves it as JSON
   at `GET /api/forecast`.
3. **Frontend** (`frontend/`) is a React dashboard that calls that endpoint
   and renders a searchable, filterable grid of cities plus a hero panel
   with a 3-day high/low trend chart. If the API isn't reachable, it falls
   back to bundled sample data so the UI is never blank.

## Quickstart (sample data, no Airflow needed)

```bash
# backend
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python seed_db.py
export DB_PATH=./NMA_Threedays_forcast_DataBase.db
uvicorn app.main:app --reload --port 8000

# frontend (new terminal)
cd frontend
npm install
npm run dev
```

Open http://localhost:5173.

## Quickstart (live Airflow data)

Point the backend at the real DB instead of the seeded one:

```bash
export DB_PATH=~/airflow/harvestedfiles/NMA_Threedays_forcast_DataBase.db
uvicorn app.main:app --reload --port 8000
```

Everything else is unchanged.
