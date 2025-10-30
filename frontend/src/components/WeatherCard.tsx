import React from 'react';
import { WeatherData } from '../hooks/useWeatherData';

interface WeatherCardProps {
  data: WeatherData;
}

const WeatherCard: React.FC<WeatherCardProps> = ({ data }) => {
  if (!data) return null;

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 mb-4 transition-all duration-300 hover:shadow-xl">
      <div className="flex justify-between items-center mb-4 pb-4 border-b border-gray-200 dark:border-gray-700">
        <h2 className="text-xl font-bold text-gray-900 dark:text-white">{data.city}</h2>
        <span className="text-2xl font-bold text-blue-600 dark:text-blue-400">{data.temperature}°C</span>
      </div>
      <div className="flex items-center mb-4">
        <span className="text-gray-600 dark:text-gray-300">{data.weatherCondition}</span>
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div className="flex items-center bg-gray-50 dark:bg-gray-700 p-3 rounded-lg">
          <span className="text-gray-600 dark:text-gray-300 mr-2">Humidity:</span>
          <span className="font-medium">{data.humidity}%</span>
        </div>
        <div className="flex items-center bg-gray-50 dark:bg-gray-700 p-3 rounded-lg">
          <span className="text-gray-600 dark:text-gray-300 mr-2">Wind:</span>
          <span className="font-medium">{data.windSpeed} km/h</span>
        </div>
        <div className="flex items-center bg-gray-50 dark:bg-gray-700 p-3 rounded-lg">
          <span className="text-gray-600 dark:text-gray-300 mr-2">Pressure:</span>
          <span className="font-medium">{data.pressure} hPa</span>
        </div>
        <div className="flex items-center bg-gray-50 dark:bg-gray-700 p-3 rounded-lg">
          <span className="text-gray-600 dark:text-gray-300 mr-2">UV Index:</span>
          <span className="font-medium">{data.uvIndex}</span>
        </div>
      </div>
    </div>
  );
};

export default WeatherCard;