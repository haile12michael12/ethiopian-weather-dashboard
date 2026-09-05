"""
Creates a local Threedays_forcast_DataBase.db with sample rows so the
API and frontend can be run/tested without waiting on a real Airflow DAG run.
Creates and seeds a local weather forecast database with sample rows so the
API and frontend can be tested without waiting on a live Airflow or fallback run.
Supports both SQLite and PostgreSQL/TimescaleDB.

Usage:
    python seed_db.py
"""
import os
import sqlite3
import sys
from datetime import datetime

DB_PATH = os.environ.get("DB_PATH", "./Threedays_forcast_DataBase.db")
# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import get_connection, init_db, DB_PATH, get_db_type

SAMPLE_ROWS = [
    # City, MinD1, MaxD1, CondD1, MinD2, MaxD2, CondD2, MinD3, MaxD3, CondD3
    ("Addis Ababa", 11, 22, "Partly Cloudy", 10, 21, "Scattered Showers", 12, 23, "Mostly Sunny"),
    ("Debre Birhan", 7, 18, "Cloudy", 6, 17, "Rain Showers", 8, 19, "Partly Cloudy"),
    ("Bahir Dar", 15, 27, "Sunny", 16, 28, "Mostly Sunny", 15, 26, "Partly Cloudy"),
    ("Gondar", 14, 28, "Sunny", 14, 29, "Sunny", 15, 27, "Mostly Sunny"),
    ("Mekelle", 12, 25, "Mostly Sunny", 11, 24, "Partly Cloudy", 12, 25, "Sunny"),
    ("Axum", 13, 27, "Sunny", 13, 28, "Sunny", 14, 26, "Mostly Sunny"),
    ("Dessie", 10, 23, "Partly Cloudy", 9, 22, "Cloudy", 10, 23, "Mostly Sunny"),
    ("Hawassa", 15, 27, "Partly Cloudy", 14, 26, "Thunderstorms", 15, 27, "Scattered Showers"),
    ("Adama", 16, 29, "Sunny", 16, 30, "Mostly Sunny", 17, 29, "Partly Cloudy"),
    ("Arba Minch", 18, 31, "Mostly Sunny", 18, 30, "Thunderstorms", 17, 29, "Rain Showers"),
    ("Jimma", 13, 24, "Rain Showers", 13, 23, "Thunderstorms", 14, 24, "Scattered Showers"),
    ("Nekemte", 12, 23, "Cloudy", 12, 22, "Rain Showers", 13, 23, "Partly Cloudy"),
    ("Dire Dawa", 22, 34, "Sunny", 23, 35, "Sunny", 22, 34, "Mostly Sunny"),
    ("Jijiga", 15, 26, "Partly Cloudy", 14, 25, "Cloudy", 15, 26, "Mostly Sunny"),
    ("Semera", 27, 41, "Sunny", 28, 42, "Sunny", 27, 40, "Sunny"),
    # City, MinD1, MaxD1, CondD1, Rain1, Wind1, MinD2, MaxD2, CondD2, Rain2, Wind2, MinD3, MaxD3, CondD3, Rain3, Wind3
    ("Addis Ababa", 11, 22, "Partly Cloudy", 40, 12, 10, 21, "Scattered Showers", 65, 14, 12, 23, "Mostly Sunny", 20, 10),
    ("Debre Birhan", 7, 18, "Cloudy", 30, 15, 6, 17, "Rain Showers", 70, 18, 8, 19, "Partly Cloudy", 25, 12),
    ("Bahir Dar", 15, 27, "Sunny", 10, 8, 16, 28, "Mostly Sunny", 15, 9, 15, 26, "Partly Cloudy", 30, 11),
    ("Gondar", 14, 28, "Sunny", 10, 10, 14, 29, "Sunny", 10, 9, 15, 27, "Mostly Sunny", 20, 12),
    ("Mekelle", 12, 25, "Mostly Sunny", 15, 14, 11, 24, "Partly Cloudy", 25, 12, 12, 25, "Sunny", 10, 10),
    ("Axum", 13, 27, "Sunny", 5, 8, 13, 28, "Sunny", 5, 7, 14, 26, "Mostly Sunny", 15, 9),
    ("Dessie", 10, 23, "Partly Cloudy", 35, 11, 9, 22, "Cloudy", 45, 13, 10, 23, "Mostly Sunny", 20, 10),
    ("Hawassa", 15, 27, "Partly Cloudy", 25, 10, 14, 26, "Thunderstorms", 80, 22, 15, 27, "Scattered Showers", 50, 12),
    ("Adama", 16, 29, "Sunny", 10, 12, 16, 30, "Mostly Sunny", 15, 11, 17, 29, "Partly Cloudy", 20, 14),
    ("Arba Minch", 18, 31, "Mostly Sunny", 20, 9, 18, 30, "Thunderstorms", 75, 20, 17, 29, "Rain Showers", 60, 14),
    ("Jimma", 13, 24, "Rain Showers", 70, 8, 13, 23, "Thunderstorms", 85, 18, 14, 24, "Scattered Showers", 55, 10),
    ("Nekemte", 12, 23, "Cloudy", 40, 12, 12, 22, "Rain Showers", 65, 15, 13, 23, "Partly Cloudy", 30, 11),
    ("Dire Dawa", 22, 34, "Sunny", 5, 16, 23, 35, "Sunny", 5, 18, 22, 34, "Mostly Sunny", 10, 15),
    ("Jijiga", 15, 26, "Partly Cloudy", 20, 14, 14, 25, "Cloudy", 35, 16, 15, 26, "Mostly Sunny", 15, 12),
    ("Semera", 27, 41, "Sunny", 0, 24, 28, 42, "Sunny", 0, 26, 27, 40, "Sunny", 0, 22),
]

CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS threedaysForcasetData(
    RecNum INTEGER PRIMARY KEY AUTOINCREMENT,
    City TEXT,
    MinTempD1 INTEGER,
    MaxTempD1 INTEGER,
    WeatherConditionD1 TEXT,
    MinTempD2 INTEGER,
    MaxTempD2 INTEGER,
    WeatherConditionD2 TEXT,
    MinTempD3 INTEGER,
    MaxTempD3 INTEGER,
    WeatherConditionD3 TEXT
);
INSERT_SQL = """
INSERT INTO weather_forecasts
(City, MinTempD1, MaxTempD1, WeatherConditionD1, RainPercentD1, WindD1,
 MinTempD2, MaxTempD2, WeatherConditionD2, RainPercentD2, WindD2,
 MinTempD3, MaxTempD3, WeatherConditionD3, RainPercentD3, WindD3,
 DataSource, QualityStatus)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'NMA', 'verified')
"""

INSERT = """
INSERT INTO threedaysForcasetData
(City, MinTempD1, MaxTempD1, WeatherConditionD1, MinTempD2, MaxTempD2, WeatherConditionD2, MinTempD3, MaxTempD3, WeatherConditionD3)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
LEGACY_INSERT_SQL = """
INSERT INTO NMAthreedaysForcasetData
(City, MinTempD1, MaxTempD1, WeatherConditionD1, RainPercentD1, WindD1,
 MinTempD2, MaxTempD2, WeatherConditionD2, RainPercentD2, WindD2,
 MinTempD3, MaxTempD3, WeatherConditionD3, RainPercentD3, WindD3,
 DataSource, QualityStatus)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'NMA', 'verified')
"""


def main():
    conn = sqlite3.connect(DB_PATH)
    conn.execute(CREATE_TABLE)
    conn.executemany(INSERT, SAMPLE_ROWS)
    conn.commit()
    conn.close()
    print(f"Seeded {len(SAMPLE_ROWS)} cities into {DB_PATH}")
    print(f"Initializing database schema ({get_db_type()})...")
    init_db()

    with get_connection() as conn:
        for row in SAMPLE_ROWS:
            conn.execute(INSERT_SQL, row)
            try:
                conn.execute(LEGACY_INSERT_SQL, row)
            except Exception:
                pass
        conn.commit()

    print(f"Seeded {len(SAMPLE_ROWS)} cities with full telemetry into {get_db_type()}.")


if __name__ == "__main__":
    main()
