import os
import sqlite3
from utils.config import Config

class WeatherModel:
    def __init__(self):
        self.DATABASE_PATH = Config.get_database_path()
    
    def get_db_connection(self):
        """Create a database connection"""
        conn = sqlite3.connect(self.DATABASE_PATH)
        conn.row_factory = sqlite3.Row  # This enables column access by name
        return conn
    
    def get_all_weather_data(self):
        """Get all weather forecast data"""
        try:
            conn = self.get_db_connection()
            weather_data = conn.execute(
                'SELECT * FROM NMAthreedaysForcasetData ORDER BY RecNum DESC'
            ).fetchall()
            conn.close()
            return [dict(row) for row in weather_data]
        except Exception as e:
            raise Exception(f"Database error: {str(e)}")
    
    def get_weather_data_by_city(self, city):
        """Get weather forecast data for a specific city"""
        try:
            conn = self.get_db_connection()
            weather_data = conn.execute(
                'SELECT * FROM NMAthreedaysForcasetData WHERE City = ?', (city,)
            ).fetchall()
            conn.close()
            return [dict(row) for row in weather_data]
        except Exception as e:
            raise Exception(f"Database error: {str(e)}")