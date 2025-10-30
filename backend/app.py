import sys
import os

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from flask_cors import CORS
from controllers.weather_controller import WeatherController

def create_app():
    """Create and configure the Flask application"""
    app = Flask(__name__)
    CORS(app)  # This will enable CORS for all routes
    
    # Initialize controller
    weather_controller = WeatherController()
    
    # Define routes
    @app.route('/api/weather', methods=['GET'])
    def get_weather_data():
        """Get all weather forecast data"""
        return weather_controller.get_weather_data()
    
    @app.route('/api/weather/<city>', methods=['GET'])
    def get_weather_by_city(city):
        """Get weather forecast data for a specific city"""
        return weather_controller.get_weather_by_city(city)
    
    @app.route('/health', methods=['GET'])
    def health_check():
        """Health check endpoint"""
        return weather_controller.health_check()
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)