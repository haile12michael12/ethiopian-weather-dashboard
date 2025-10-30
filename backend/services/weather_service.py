from models.weather_model import WeatherModel

class WeatherService:
    def __init__(self):
        self.weather_model = WeatherModel()
    
    def get_all_weather_data(self):
        """Get all weather forecast data"""
        try:
            weather_data = self.weather_model.get_all_weather_data()
            return {
                'success': True,
                'data': weather_data
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_weather_data_by_city(self, city):
        """Get weather forecast data for a specific city"""
        try:
            weather_data = self.weather_model.get_weather_data_by_city(city)
            if not weather_data:
                return {
                    'success': False,
                    'error': 'City not found'
                }
            return {
                'success': True,
                'data': weather_data
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }