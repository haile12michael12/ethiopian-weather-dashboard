"""
Universal Database Access Layer for Ethiopian Weather Dashboard.
Supports:
1. PostgreSQL / TimescaleDB (via DATABASE_URL = 'postgresql://...')
2. SQLite (via DB_PATH or default fallback)

Provides transparent SQL parameter translation (? -> %s for Postgres),
row-to-dict abstraction, and automatic hypertable initialization.
"""
import os
import re
import logging
from contextlib import contextmanager
from typing import Generator, Any, Optional

logger = logging.getLogger(__name__)

# Fallback local paths
DEFAULT_LOCAL_DB = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "Threedays_forcast_DataBase.db"
)
AIRFLOW_DB_PATH = os.path.join(
    os.path.expanduser("~"), "airflow", "harvestedfiles", "Threedays_forcast_DataBase.db"
)

DATABASE_URL = os.environ.get("DATABASE_URL")
DB_PATH = os.environ.get("DB_PATH") or (AIRFLOW_DB_PATH if os.path.exists(AIRFLOW_DB_PATH) else DEFAULT_LOCAL_DB)


def is_postgres() -> bool:
    """Checks if the configured database is PostgreSQL/TimescaleDB."""
    return bool(DATABASE_URL and (DATABASE_URL.startswith("postgres://") or DATABASE_URL.startswith("postgresql://")))


def get_db_type() -> str:
    """Returns human-readable name of active database engine."""
    if is_postgres():
        return "PostgreSQL / TimescaleDB"
    return "SQLite"


class PostgresCursorWrapper:
    """Wraps psycopg2 DictCursor to support parameter translation (? -> %s)."""
    def __init__(self, cursor):
        self._cursor = cursor

    def execute(self, query: str, params: Any = None):
        # Convert ? placeholders to %s for PostgreSQL
        pg_query = query.replace("?", "%s")
        if params is not None:
            if isinstance(params, (list, tuple)):
                return self._cursor.execute(pg_query, params)
            return self._cursor.execute(pg_query, (params,))
        return self._cursor.execute(pg_query)

    def executemany(self, query: str, seq_of_params: Any):
        pg_query = query.replace("?", "%s")
        return self._cursor.executemany(pg_query, seq_of_params)

    def fetchone(self):
        return self._cursor.fetchone()

    def fetchall(self):
        return self._cursor.fetchall()

    def __iter__(self):
        return iter(self._cursor)


class PostgresConnectionWrapper:
    """Wraps psycopg2 connection to provide sqlite3-like context and cursor behavior."""
    def __init__(self, conn):
        self._conn = conn

    def cursor(self):
        import psycopg2.extras
        return PostgresCursorWrapper(self._conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor))

    def execute(self, query: str, params: Any = None):
        cur = self.cursor()
        cur.execute(query, params)
        return cur

    def executemany(self, query: str, seq_of_params: Any):
        cur = self.cursor()
        cur.executemany(query, seq_of_params)
        return cur

    def commit(self):
        self._conn.commit()

    def rollback(self):
        self._conn.rollback()

    def close(self):
        self._conn.close()


@contextmanager
def get_connection():
    """
    Context manager that yields a database connection.
    Works seamlessly with both PostgreSQL and SQLite.
    """
    if is_postgres():
        try:
            import psycopg2
            conn = psycopg2.connect(DATABASE_URL)
            wrapped = PostgresConnectionWrapper(conn)
            try:
                yield wrapped
            finally:
                wrapped.close()
        except ImportError:
            logger.error("psycopg2 is not installed. Falling back to SQLite.")
            import sqlite3
            conn = sqlite3.connect(DB_PATH)
            conn.row_factory = sqlite3.Row
            try:
                yield conn
            finally:
                conn.close()
    else:
        import sqlite3
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()


def init_db():
    """
    Initializes database schema with support for TimescaleDB hypertables,
    standardized column definitions, and backward-compatible views.
    """
    with get_connection() as conn:
        if is_postgres():
            # PostgreSQL / TimescaleDB Schema
            conn.execute("""
                CREATE TABLE IF NOT EXISTS weather_forecasts (
                    RecNum SERIAL PRIMARY KEY,
                    City VARCHAR(100) NOT NULL,
                    MinTempD1 INTEGER NOT NULL,
                    MaxTempD1 INTEGER NOT NULL,
                    WeatherConditionD1 VARCHAR(100) NOT NULL,
                    RainPercentD1 INTEGER DEFAULT 0,
                    WindD1 INTEGER DEFAULT 0,
                    MinTempD2 INTEGER NOT NULL,
                    MaxTempD2 INTEGER NOT NULL,
                    WeatherConditionD2 VARCHAR(100) NOT NULL,
                    RainPercentD2 INTEGER DEFAULT 0,
                    WindD2 INTEGER DEFAULT 0,
                    MinTempD3 INTEGER NOT NULL,
                    MaxTempD3 INTEGER NOT NULL,
                    WeatherConditionD3 VARCHAR(100) NOT NULL,
                    RainPercentD3 INTEGER DEFAULT 0,
                    WindD3 INTEGER DEFAULT 0,
                    DataSource VARCHAR(50) DEFAULT 'NMA',
                    QualityStatus VARCHAR(50) DEFAULT 'verified',
                    RecordedAt TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """)

            # Try activating TimescaleDB hypertable if extension exists
            try:
                conn.execute("CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;")
                conn.execute("SELECT create_hypertable('weather_forecasts', 'recordedat', if_not_exists => TRUE);")
                logger.info("TimescaleDB hypertable initialized on weather_forecasts(recordedat)")
            except Exception as e:
                logger.info(f"TimescaleDB extension not active (standard PostgreSQL used): {e}")

            # Create indexing & backward-compatible views
            conn.execute("CREATE INDEX IF NOT EXISTS idx_weather_city_time ON weather_forecasts (City, RecordedAt DESC);")
            conn.execute("CREATE OR REPLACE VIEW NMAthreedaysForcasetData AS SELECT * FROM weather_forecasts;")
            conn.execute("CREATE OR REPLACE VIEW threedaysForcasetData AS SELECT * FROM weather_forecasts;")
            conn.commit()

        else:
            # SQLite Schema
            conn.execute("""
                CREATE TABLE IF NOT EXISTS weather_forecasts (
                    RecNum INTEGER PRIMARY KEY AUTOINCREMENT,
                    City TEXT NOT NULL,
                    MinTempD1 INTEGER NOT NULL,
                    MaxTempD1 INTEGER NOT NULL,
                    WeatherConditionD1 TEXT NOT NULL,
                    RainPercentD1 INTEGER DEFAULT 0,
                    WindD1 INTEGER DEFAULT 0,
                    MinTempD2 INTEGER NOT NULL,
                    MaxTempD2 INTEGER NOT NULL,
                    WeatherConditionD2 TEXT NOT NULL,
                    RainPercentD2 INTEGER DEFAULT 0,
                    WindD2 INTEGER DEFAULT 0,
                    MinTempD3 INTEGER NOT NULL,
                    MaxTempD3 INTEGER NOT NULL,
                    WeatherConditionD3 TEXT NOT NULL,
                    RainPercentD3 INTEGER DEFAULT 0,
                    WindD3 INTEGER DEFAULT 0,
                    DataSource TEXT DEFAULT 'NMA',
                    QualityStatus TEXT DEFAULT 'verified',
                    RecordedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            # Ensure NMAthreedaysForcasetData table/view exists for backward compatibility
            conn.execute("""
                CREATE TABLE IF NOT EXISTS NMAthreedaysForcasetData (
                    RecNum INTEGER PRIMARY KEY AUTOINCREMENT,
                    City TEXT NOT NULL,
                    MinTempD1 INTEGER NOT NULL,
                    MaxTempD1 INTEGER NOT NULL,
                    WeatherConditionD1 TEXT NOT NULL,
                    RainPercentD1 INTEGER DEFAULT 0,
                    WindD1 INTEGER DEFAULT 0,
                    MinTempD2 INTEGER NOT NULL,
                    MaxTempD2 INTEGER NOT NULL,
                    WeatherConditionD2 TEXT NOT NULL,
                    RainPercentD2 INTEGER DEFAULT 0,
                    WindD2 INTEGER DEFAULT 0,
                    MinTempD3 INTEGER NOT NULL,
                    MaxTempD3 INTEGER NOT NULL,
                    WeatherConditionD3 TEXT NOT NULL,
                    RainPercentD3 INTEGER DEFAULT 0,
                    WindD3 INTEGER DEFAULT 0,
                    DataSource TEXT DEFAULT 'NMA',
                    QualityStatus TEXT DEFAULT 'verified',
                    RecordedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            # Also ensure threedaysForcasetData exists
            conn.execute("""
                CREATE TABLE IF NOT EXISTS threedaysForcasetData (
                    RecNum INTEGER PRIMARY KEY AUTOINCREMENT,
                    City TEXT NOT NULL,
                    MinTempD1 INTEGER NOT NULL,
                    MaxTempD1 INTEGER NOT NULL,
                    WeatherConditionD1 TEXT NOT NULL,
                    RainPercentD1 INTEGER DEFAULT 0,
                    WindD1 INTEGER DEFAULT 0,
                    MinTempD2 INTEGER NOT NULL,
                    MaxTempD2 INTEGER NOT NULL,
                    WeatherConditionD2 TEXT NOT NULL,
                    RainPercentD2 INTEGER DEFAULT 0,
                    WindD2 INTEGER DEFAULT 0,
                    MinTempD3 INTEGER NOT NULL,
                    MaxTempD3 INTEGER NOT NULL,
                    WeatherConditionD3 TEXT NOT NULL,
                    RainPercentD3 INTEGER DEFAULT 0,
                    WindD3 INTEGER DEFAULT 0,
                    DataSource TEXT DEFAULT 'NMA',
                    QualityStatus TEXT DEFAULT 'verified',
                    RecordedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            # Add missing columns to existing SQLite tables if migrating from older versions
            for tbl in ["NMAthreedaysForcasetData", "threedaysForcasetData", "weather_forecasts"]:
                try:
                    cur = conn.execute(f"PRAGMA table_info({tbl})")
                    existing_cols = {row[1] for row in cur.fetchall()}
                    for col, col_type in [
                        ("RainPercentD1", "INTEGER DEFAULT 0"),
                        ("WindD1", "INTEGER DEFAULT 0"),
                        ("RainPercentD2", "INTEGER DEFAULT 0"),
                        ("WindD2", "INTEGER DEFAULT 0"),
                        ("RainPercentD3", "INTEGER DEFAULT 0"),
                        ("WindD3", "INTEGER DEFAULT 0"),
                        ("DataSource", "TEXT DEFAULT 'NMA'"),
                        ("QualityStatus", "TEXT DEFAULT 'verified'"),
                        ("RecordedAt", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"),
                    ]:
                        if col not in existing_cols:
                            conn.execute(f"ALTER TABLE {tbl} ADD COLUMN {col} {col_type};")
                except Exception as ex:
                    logger.debug(f"Column check notice for {tbl}: {ex}")

            conn.commit()


def table_exists() -> bool:
    """Checks if any valid forecast table exists in the active database."""
    with get_connection() as conn:
        if is_postgres():
            cur = conn.execute(
                "SELECT table_name FROM information_schema.tables WHERE table_name IN ('weather_forecasts', 'nmathreedaysforcasetdata')"
            )
            return cur.fetchone() is not None
        else:
            cur = conn.execute(
                "SELECT name FROM sqlite_master WHERE type IN ('table', 'view') AND name IN ('NMAthreedaysForcasetData', 'threedaysForcasetData', 'weather_forecasts')"
            )
            return cur.fetchone() is not None
