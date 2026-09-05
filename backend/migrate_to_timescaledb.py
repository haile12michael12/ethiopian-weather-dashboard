"""
Migration Tool: SQLite -> PostgreSQL / TimescaleDB.
Transfers legacy weather records into TimescaleDB with data quality verification.

Usage:
    python migrate_to_timescaledb.py --sqlite-path ./Threedays_forcast_DataBase.db --target-url postgresql://postgres:postgres@localhost:5432/weather_db
"""
import argparse
import os
import sys
import sqlite3
import logging
from datetime import datetime

# Add parent directory to path so imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.pipeline.quality import validate_batch

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def migrate(sqlite_path: str, target_url: str):
    logger.info(f"Starting migration from SQLite ({sqlite_path}) -> TimescaleDB/Postgres")

    if not os.path.exists(sqlite_path):
        logger.error(f"SQLite source file '{sqlite_path}' does not exist.")
        sys.exit(1)

    try:
        import psycopg2
        import psycopg2.extras
    except ImportError:
        logger.error("psycopg2 is required for TimescaleDB migration. Run: pip install psycopg2-binary")
        sys.exit(1)

    # 1. Read SQLite records
    sqlite_conn = sqlite3.connect(sqlite_path)
    sqlite_conn.row_factory = sqlite3.Row
    cur = sqlite_conn.cursor()

    # Determine source table
    cur.execute("SELECT name FROM sqlite_master WHERE type IN ('table', 'view') AND name IN ('NMAthreedaysForcasetData', 'threedaysForcasetData', 'weather_forecasts')")
    found = cur.fetchone()
    if not found:
        logger.error("No compatible weather forecast table found in SQLite source.")
        sys.exit(1)

    src_table = found[0]
    logger.info(f"Reading from SQLite table '{src_table}'...")
    rows = cur.execute(f"SELECT * FROM {src_table}").fetchall()
    raw_records = [dict(r) for r in rows]
    logger.info(f"Extracted {len(raw_records)} records from SQLite.")

    # 2. Quality Verification
    logger.info("Running records through Data Quality Engine...")
    validated_records, quality_report = validate_batch(raw_records)
    logger.info(
        f"Quality Check Results: {quality_report.verified} verified, "
        f"{quality_report.corrected} auto-corrected, {quality_report.rejected} rejected."
    )

    # 3. Connect to PostgreSQL / TimescaleDB & Initialize Schema
    logger.info(f"Connecting to target database: {target_url}...")
    pg_conn = psycopg2.connect(target_url)
    pg_cur = pg_conn.cursor()

    # Create table
    pg_cur.execute("""
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

    # Activate TimescaleDB hypertable if extension is available
    try:
        pg_cur.execute("CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;")
        pg_cur.execute("SELECT create_hypertable('weather_forecasts', 'recordedat', if_not_exists => TRUE);")
        logger.info("TimescaleDB hypertable enabled.")
    except Exception as e:
        logger.info(f"TimescaleDB hypertable notice: {e}")

    pg_cur.execute("CREATE INDEX IF NOT EXISTS idx_weather_city_time ON weather_forecasts (City, RecordedAt DESC);")
    pg_cur.execute("CREATE OR REPLACE VIEW NMAthreedaysForcasetData AS SELECT * FROM weather_forecasts;")
    pg_cur.execute("CREATE OR REPLACE VIEW threedaysForcasetData AS SELECT * FROM weather_forecasts;")
    pg_conn.commit()

    # 4. Bulk Insert Validated Records
    insert_sql = """
        INSERT INTO weather_forecasts (
            City, MinTempD1, MaxTempD1, WeatherConditionD1, RainPercentD1, WindD1,
            MinTempD2, MaxTempD2, WeatherConditionD2, RainPercentD2, WindD2,
            MinTempD3, MaxTempD3, WeatherConditionD3, RainPercentD3, WindD3,
            DataSource, QualityStatus, RecordedAt
        ) VALUES (
            %(City)s, %(MinTempD1)s, %(MaxTempD1)s, %(WeatherConditionD1)s, %(RainPercentD1)s, %(WindD1)s,
            %(MinTempD2)s, %(MaxTempD2)s, %(WeatherConditionD2)s, %(RainPercentD2)s, %(WindD2)s,
            %(MinTempD3)s, %(MaxTempD3)s, %(WeatherConditionD3)s, %(RainPercentD3)s, %(WindD3)s,
            %(DataSource)s, %(QualityStatus)s, %(RecordedAt)s
        );
    """

    payloads = []
    for r in validated_records:
        d = r.to_dict()
        d["RecordedAt"] = datetime.utcnow()
        payloads.append(d)

    psycopg2.extras.execute_batch(pg_cur, insert_sql, payloads)
    pg_conn.commit()

    # 5. Verify Target Count
    pg_cur.execute("SELECT COUNT(*) FROM weather_forecasts;")
    count = pg_cur.fetchone()[0]
    logger.info(f"Migration completed successfully! Total records in TimescaleDB/PostgreSQL: {count}")

    sqlite_conn.close()
    pg_conn.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Migrate SQLite to TimescaleDB/PostgreSQL")
    parser.add_argument("--sqlite-path", default=os.environ.get("DB_PATH", "./Threedays_forcast_DataBase.db"))
    parser.add_argument("--target-url", default=os.environ.get("DATABASE_URL"))

    args = parser.parse_args()
    if not args.target_url:
        print("Please provide --target-url or set DATABASE_URL environment variable.")
        print("Example: python migrate_to_timescaledb.py --target-url postgresql://postgres:secret@localhost:5432/weather")
        sys.exit(1)

    migrate(args.sqlite_path, args.target_url)
