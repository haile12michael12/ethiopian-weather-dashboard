from flask import jsonify
from services.weather_service import WeatherService

class WeatherController:
    def __init__(self):
        self.weather_service = WeatherService()
    
    def get_weather_data(self):
        """Get all weather forecast data"""
        try:
            result = self.weather_service.get_all_weather_data()
            if result['success']:
                return jsonify(result), 200
            else:
                return jsonify(result), 500
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    def get_weather_by_city(self, city):
        """Get weather forecast data for a specific city"""
        try:
            result = self.weather_service.get_weather_data_by_city(city)
            if result['success']:
                return jsonify(result), 200
            elif 'City not found' in result.get('error', ''):
                return jsonify(result), 404
            else:
                return jsonify(result), 500
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    def health_check(self):
        """Health check endpoint"""
        return jsonify({
            'status': 'healthy',
            'message': 'Weather API is running'
        }), 200