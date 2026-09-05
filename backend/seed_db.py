"""
Creates a local Threedays_forcast_DataBase.db with sample rows so the
API and frontend can be run/tested without waiting on a real Airflow DAG run.

Usage:
    python seed_db.py
"""
import os
import sqlite3

DB_PATH = os.environ.get("DB_PATH", "./Threedays_forcast_DataBase.db")

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
"""

INSERT = """
INSERT INTO threedaysForcasetData
(City, MinTempD1, MaxTempD1, WeatherConditionD1, MinTempD2, MaxTempD2, WeatherConditionD2, MinTempD3, MaxTempD3, WeatherConditionD3)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
"""

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.execute(CREATE_TABLE)
    conn.executemany(INSERT, SAMPLE_ROWS)
    conn.commit()
    conn.close()
    print(f"Seeded {len(SAMPLE_ROWS)} cities into {DB_PATH}")

if __name__ == "__main__":
    main()
