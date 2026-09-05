"""
Airflow DAG: Resilient Ethiopian Weather Ingestion Pipeline.
Performs:
1. Primary NMA scrape attempt (ethiomet.gov.et)
2. Automated Pydantic data quality and anomaly checks
3. Secondary fallback ingestion via Open-Meteo API when NMA is unavailable or incomplete
4. Atomic storage into PostgreSQL/TimescaleDB or SQLite
"""
import os
import json
import requests
import xmltodict
import pandas as pd
import requests.exceptions as requests_exceptions
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
import save_metadata as Metadata
import sys
import logging
from datetime import datetime
import pendulum
from airflow.decorators import dag, task
import pendulum
import csv
import sqlite3
from airflow.providers.sqlite.operators.sqlite import SqliteOperator
from airflow.providers.sqlite.hooks.sqlite import SqliteHook

from bs4 import BeautifulSoup
# Add project root and backend to python path for task execution
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND_DIR = os.path.join(PROJECT_ROOT, "backend")
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

logger = logging.getLogger(__name__)

forcast_URL = 'http://www.ethiomet.gov.et/forecasts/three_day_forecast' 
home_directory = os.path.expanduser( '~' )
forcast_FOLDER = os.path.join(home_directory, "airflow","harvestedfiles")

@dag(
    dag_id='NMA_threeDays_forcast_data_scraper',
    dag_id="NMA_threeDays_forcast_data_scraper",
    schedule_interval="@daily",
    start_date=pendulum.datetime(2022, 5, 30),
    tags=['scrap three days weather forcast everyday from National Methrology Agency'],
    tags=["ethiopia", "weather", "nma", "resilient_pipeline", "timescaledb"],
    catchup=False,
    max_active_runs=1,
)
def nma_web_scrapper():
def resilient_ethiopian_weather_pipeline():

    @task()
    def get_forcasts_scraper():
        threeDayspage = requests.get(forcast_URL)
        dfs = pd.read_html(threeDayspage.text)[2]
        pages = requests.get(forcast_URL)
        found_pages = BeautifulSoup(pages.text, 'lxml')
        
        titlefound = found_pages.table.table
        dataTitle = titlefound.find_all(colspan="3")
        data2 = []
       
        for listTitle in dataTitle[0:]:
            data2.append(listTitle.getText())
        firstDate = data2[0]
        secondDate = data2[1]
        thirdDate = data2[2]
        tages_between = found_pages.table.table
        tages_AsofDate = tages_between.h3.getText()
        tages_AsofDate = tages_AsofDate.replace("\n", " ")
        filename = f"NMA Three Day Forecast {tages_AsofDate}.csv"
        df_csv_file = f'TemporaryFile.csv'
        file_path = os.path.join(forcast_FOLDER, filename)
    def fetch_primary_nma() -> dict:
        """Attempts to scrape Ethiopian National Meteorology Agency portal."""
        from app.pipeline.sources.nma import fetch_nma_forecast, NMAScraperError
        try:
            records = fetch_nma_forecast(max_retries=2, retry_delay=1.0)
            return {"status": "success", "records": records, "source": "NMA"}
        except (NMAScraperError, Exception) as exc:
            logger.warning(f"Primary NMA portal unavailable: {exc}")
            return {"status": "failed", "records": [], "error": str(exc), "source": "NMA"}

        tages_between_specifc = tages_between.find_all('img')
        data=[]
        for listT in tages_between_specifc[1:]:
            if(listT.get('title') == None):
                data.append('Mostly Sunny')
            else:
                data.append(listT.get('title')) 
        df = pd.DataFrame(columns=['City',f"Min Temp {firstDate}",f"Max Temp {firstDate}",f"Weather Condition {firstDate}",f"Min Temp {secondDate}",f"Max Temp {secondDate}",f"Weather Condition {secondDate}",f"Min Temp {thirdDate}",f"Max Temp {thirdDate}",f"Weather Condition {thirdDate}"]) 
        counter = 0                 
        for row in dfs.values:
            if len(row) <= 33:
                num = row[0]
                city = row[1]
                MinTempD1 = row[2]
                MaxTempD1 = row[3]
                WeatherConditionD1 = data[counter]
                MinTempD2 = row[5]
                MaxTempD2 = row[6]
                WeatherConditionD2 = data[counter+1]
                MinTempD3 = row[8]
                MaxTempD3 = row[9]
                WeatherConditionD3 = data[counter+2]
                counter = counter + 3
                df = df.append({'City': city, f"Min Temp {firstDate}": MinTempD1, f"Max Temp {firstDate}": MaxTempD1, f"Weather Condition {firstDate}": WeatherConditionD1, f"Min Temp {secondDate}": MinTempD2, f"Max Temp {secondDate}": MaxTempD2, f"Weather Condition {secondDate}":  WeatherConditionD2, f"Min Temp {thirdDate}": MinTempD3, f"Max Temp {thirdDate}": MaxTempD3, f"Weather Condition {thirdDate}": WeatherConditionD3}, ignore_index=True)
        dfd = df
        df.to_csv(df_csv_file, index=False, encoding='utf-8')
        fileOpenTwo = open(f'{df_csv_file}')
        ContentRead = csv.reader(fileOpenTwo)
        conn = sqlite3.connect(f'{forcast_FOLDER}/NMA_Threedays_forcast_DataBase.db', timeout=20)
        cursor = conn.cursor()
        create_table = '''CREATE TABLE IF NOT EXISTS NMAthreedaysForcasetData(
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
                '''
        insert_records = "INSERT INTO NMAthreedaysForcasetData (City, MinTempD1, MaxTempD1, WeatherConditionD1, MinTempD2, MaxTempD2, WeatherConditionD2, MinTempD3, MaxTempD3, WeatherConditionD3) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
        cursor.executemany(insert_records, ContentRead)
# Committing the changes
        conn.commit()
        conn.close()      
        dfd.to_csv(file_path, index=False, encoding='utf-8')
        #call save metadata function
        Metadata.saveMetadata(forcast_URL, filename, "csv", len(df), "1.0", "National Metrology Agency", "Three days Weather Forcast", ["NMA", "Weather Forcast"])
    forcast_dailydata = get_forcasts_scraper()
  
scrapping = nma_web_scrapper()
    @task()
    def validate_and_fallback_open_meteo(nma_result: dict) -> list:
        """Runs quality checks and fetches Open-Meteo fallback for any missing or failed cities."""
        from app.pipeline.cities import ETHIOPIAN_CITIES
        from app.pipeline.sources.open_meteo import fetch_all_cities_open_meteo
        from app.pipeline.quality import validate_batch

        records = nma_result.get("records", [])
        found_cities = {r["City"] for r in records}
        target_cities = set(ETHIOPIAN_CITIES.keys())
        missing_cities = target_cities - found_cities

        if missing_cities:
            logger.info(f"Triggering Open-Meteo fallback for {len(missing_cities)} cities: {missing_cities}")
            fallback_records = fetch_all_cities_open_meteo(cities=list(missing_cities))
            records.extend(fallback_records)

        # Run records through Pydantic data quality and anomaly validation
        validated, report = validate_batch(records)
        logger.info(f"Quality validation complete. Verified: {report.verified}, Corrected: {report.corrected}, Rejected: {report.rejected}")

        return [v.to_dict() for v in validated]

    @task()
    def persist_to_database(validated_records: list) -> dict:
        """Stores validated forecasts into PostgreSQL/TimescaleDB or SQLite."""
        from app.database import get_connection, init_db, is_postgres

        init_db()
        if not validated_records:
            raise ValueError("No valid forecast records to persist.")

        with get_connection() as conn:
            for d in validated_records:
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

        nma_count = sum(1 for r in validated_records if r["DataSource"] == "NMA")
        fallback_count = sum(1 for r in validated_records if r["DataSource"] != "NMA")

        return {
            "total_saved": len(validated_records),
            "nma_count": nma_count,
            "fallback_count": fallback_count,
            "persisted_at": datetime.utcnow().isoformat(),
        }

    # Pipeline task dependencies
    nma_data = fetch_primary_nma()
    validated_data = validate_and_fallback_open_meteo(nma_data)
    persist_to_database(validated_data)


scrapping = resilient_ethiopian_weather_pipeline()