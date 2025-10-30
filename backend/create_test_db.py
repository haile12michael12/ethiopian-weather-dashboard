import os
import sqlite3
from .utils.config import Config

def create_test_database():
    """Create a test database with mock weather data"""
    # Create the database directory if it doesn't exist
    forcast_FOLDER = Config.create_database_directory()
    DATABASE_PATH = Config.get_database_path()
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # Create the table
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

    # Insert mock data
    mock_data = [
        ("Addis Ababa", 15, 25, "Sunny", 16, 26, "Partly Cloudy", 14, 24, "Rainy"),
        ("Dire Dawa", 20, 32, "Hot", 21, 33, "Sunny", 19, 31, "Partly Cloudy"),
        ("Mekelle", 12, 22, "Cloudy", 13, 23, "Sunny", 11, 21, "Windy"),
        ("Bahir Dar", 14, 24, "Sunny", 15, 25, "Partly Cloudy", 13, 23, "Rainy"),
        ("Gondar", 13, 23, "Partly Cloudy", 14, 24, "Sunny", 12, 22, "Cloudy")
    ]

    insert_records = "INSERT INTO NMAthreedaysForcasetData (City, MinTempD1, MaxTempD1, WeatherConditionD1, MinTempD2, MaxTempD2, WeatherConditionD2, MinTempD3, MaxTempD3, WeatherConditionD3) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
    cursor.executemany(insert_records, mock_data)

    # Commit changes and close connection
    conn.commit()
    conn.close()

    print(f"Test database created successfully at {DATABASE_PATH}")

if __name__ == "__main__":
    create_test_database()