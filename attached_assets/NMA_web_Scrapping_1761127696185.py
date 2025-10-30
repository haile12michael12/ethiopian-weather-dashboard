import os
import json
import requests
import xmltodict
import pandas as pd
import requests.exceptions as requests_exceptions
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
import save_metadata as Metadata
from airflow.decorators import dag, task
import pendulum
import csv
import sqlite3
from airflow.providers.sqlite.operators.sqlite import SqliteOperator
from airflow.providers.sqlite.hooks.sqlite import SqliteHook

from bs4 import BeautifulSoup


forcast_URL = 'http://www.ethiomet.gov.et/forecasts/three_day_forecast' 
home_directory = os.path.expanduser( '~' )
forcast_FOLDER = os.path.join(home_directory, "airflow","harvestedfiles")

@dag(
    dag_id='NMA_threeDays_forcast_data_scraper',
    schedule_interval="@daily",
    start_date=pendulum.datetime(2022, 5, 30),
    tags=['scrap three days weather forcast everyday from National Methrology Agency'],
    catchup=False,
)
def nma_web_scrapper():

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