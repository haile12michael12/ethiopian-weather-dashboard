import os
import json
import requests
import xmltodict
import pandas as pd
import requests.exceptions as requests_exceptions
import csv
import sqlite3
from bs4 import BeautifulSoup

forcast_URL = 'http://www.ethiomet.gov.et/forecasts/three_day_forecast' 
home_directory = os.path.expanduser( '~' )
forcast_FOLDER = os.path.join(home_directory, "airflow","harvestedfiles")

def get_forcasts_scraper():
    try:
        threeDayspage = requests.get(forcast_URL)
        dfs = pd.read_html(threeDayspage.text)[2]
        pages = requests.get(forcast_URL)
        found_pages = BeautifulSoup(pages.text, 'lxml')
        
        # Check if the expected elements exist
        if not found_pages.table or not found_pages.table.table:
            print("Could not find expected table structure in the page")
            return None
            
        titlefound = found_pages.table.table
        dataTitle = titlefound.find_all(colspan="3")
        data2 = []
       
        for listTitle in dataTitle[0:]:
            data2.append(listTitle.getText())
            
        if len(data2) < 3:
            print("Could not extract date information")
            return None
            
        firstDate = data2[0]
        secondDate = data2[1]
        thirdDate = data2[2]
        tages_between = found_pages.table.table
        tages_AsofDate = tages_between.h3.getText() if tages_between.h3 else "Unknown Date"
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
        
        # Create empty DataFrame with proper column structure
        df_data = []
        counter = 0                 
        for row in dfs.values:
            if len(row) <= 33:
                num = row[0]
                city = row[1]
                MinTempD1 = row[2]
                MaxTempD1 = row[3]
                WeatherConditionD1 = data[counter] if counter < len(data) else 'Unknown'
                MinTempD2 = row[5]
                MaxTempD2 = row[6]
                WeatherConditionD2 = data[counter+1] if counter+1 < len(data) else 'Unknown'
                MinTempD3 = row[8]
                MaxTempD3 = row[9]
                WeatherConditionD3 = data[counter+2] if counter+2 < len(data) else 'Unknown'
                counter = counter + 3
                df_data.append({
                    'City': city, 
                    f"Min Temp {firstDate}": MinTempD1, 
                    f"Max Temp {firstDate}": MaxTempD1, 
                    f"Weather Condition {firstDate}": WeatherConditionD1, 
                    f"Min Temp {secondDate}": MinTempD2, 
                    f"Max Temp {secondDate}": MaxTempD2, 
                    f"Weather Condition {secondDate}":  WeatherConditionD2, 
                    f"Min Temp {thirdDate}": MinTempD3, 
                    f"Max Temp {thirdDate}": MaxTempD3, 
                    f"Weather Condition {thirdDate}": WeatherConditionD3
                })
        
        # Create DataFrame from the collected data
        df = pd.DataFrame(df_data)
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
        cursor.execute(create_table)
        insert_records = "INSERT INTO NMAthreedaysForcasetData (City, MinTempD1, MaxTempD1, WeatherConditionD1, MinTempD2, MaxTempD2, WeatherConditionD2, MinTempD3, MaxTempD3, WeatherConditionD3) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
        # Skip the header row
        next(ContentRead, None)
        cursor.executemany(insert_records, ContentRead)
        # Committing the changes
        conn.commit()
        conn.close()      
        dfd.to_csv(file_path, index=False, encoding='utf-8')
        print("Data successfully scraped and saved to database")
        return df
    except Exception as e:
        print(f"Error occurred: {e}")
        return None

# Run the scraper function
if __name__ == "__main__":
    result = get_forcasts_scraper()
    if result is not None:
        print("Scraping completed successfully")
    else:
        print("Scraping failed")