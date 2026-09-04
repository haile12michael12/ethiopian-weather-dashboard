"""
SQLite access layer.

Points at the database file the Airflow DAG (NMA_web_Scrapping.py) writes to:
  ~/airflow/harvestedfiles/NMA_Threedays_forcast_DataBase.db

Override the path with the DB_PATH environment variable, e.g. when running
the API next to a copy of the file instead of on the Airflow host.
"""
import os
import sqlite3
from contextlib import contextmanager

DEFAULT_DB_PATH = os.path.join(
    os.path.expanduser("~"), "airflow", "harvestedfiles", "NMA_Threedays_forcast_DataBase.db"
)
DB_PATH = os.environ.get("DB_PATH", DEFAULT_DB_PATH)


@contextmanager
def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def table_exists() -> bool:
    with get_connection() as conn:
        cur = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='NMAthreedaysForcasetData'"
        )
        return cur.fetchone() is not None
