import { useState, useEffect } from 'react';
import useWeatherData, { WeatherData } from '../hooks/useWeatherData';
import WeatherCard from './WeatherCard';
import { mockWeatherData } from '../testData';

const WeatherDashboard: React.FC = () => {
  const { weatherData, loading, error } = useWeatherData();
  const [displayData, setDisplayData] = useState<WeatherData[]>([]);

  useEffect(() => {
    if (weatherData && weatherData.length > 0) {
      setDisplayData(weatherData);
    } else if (!loading && (error || weatherData?.length === 0)) {
      // Use mock data if there's an error or no data
      console.log('Using mock data for display');
      setDisplayData(mockWeatherData);
    }
  }, [weatherData, loading, error]);

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-xl text-gray-600 dark:text-gray-300">Loading weather data...</div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {displayData.map((cityData) => (
          <WeatherCard key={cityData.id} data={cityData} />
        ))}
      </div>
    </div>
  );
};

export default WeatherDashboard;