import os
import sqlite3
import json
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

# Database configuration
home_directory = os.path.expanduser('~')
forcast_FOLDER = os.path.join(home_directory, "airflow", "harvestedfiles")
DATABASE_PATH = os.path.join(forcast_FOLDER, "NMA_Threedays_forcast_DataBase.db")

def get_db_connection():
    """Create a database connection"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row  # This enables column access by name
    return conn

@app.route('/api/weather', methods=['GET'])
def get_weather_data():
    """Get all weather forecast data"""
    try:
        conn = get_db_connection()
        # Get the latest data by selecting the most recent entries
        weather_data = conn.execute(
            'SELECT * FROM NMAthreedaysForcasetData ORDER BY RecNum DESC'
        ).fetchall()
        conn.close()
        
        # Convert to list of dictionaries
        result = []
        for row in weather_data:
            result.append({
                'RecNum': row['RecNum'],
                'City': row['City'],
                'MinTempD1': row['MinTempD1'],
                'MaxTempD1': row['MaxTempD1'],
                'WeatherConditionD1': row['WeatherConditionD1'],
                'MinTempD2': row['MinTempD2'],
                'MaxTempD2': row['MaxTempD2'],
                'WeatherConditionD2': row['WeatherConditionD2'],
                'MinTempD3': row['MinTempD3'],
                'MaxTempD3': row['MaxTempD3'],
                'WeatherConditionD3': row['WeatherConditionD3']
            })
        
        return jsonify({
            'success': True,
            'data': result
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/weather/<city>', methods=['GET'])
def get_weather_by_city(city):
    """Get weather forecast data for a specific city"""
    try:
        conn = get_db_connection()
        weather_data = conn.execute(
            'SELECT * FROM NMAthreedaysForcasetData WHERE City = ?', (city,)
        ).fetchall()
        conn.close()
        
        if not weather_data:
            return jsonify({
                'success': False,
                'error': 'City not found'
            }), 404
        
        # Convert to list of dictionaries
        result = []
        for row in weather_data:
            result.append({
                'RecNum': row['RecNum'],
                'City': row['City'],
                'MinTempD1': row['MinTempD1'],
                'MaxTempD1': row['MaxTempD1'],
                'WeatherConditionD1': row['WeatherConditionD1'],
                'MinTempD2': row['MinTempD2'],
                'MaxTempD2': row['MaxTempD2'],
                'WeatherConditionD2': row['WeatherConditionD2'],
                'MinTempD3': row['MinTempD3'],
                'MaxTempD3': row['MaxTempD3'],
                'WeatherConditionD3': row['WeatherConditionD3']
            })
        
        return jsonify({
            'success': True,
            'data': result
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'Weather API is running'
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)