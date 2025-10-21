import { useState, useEffect } from 'react';
import useWeatherData from '../hooks/useWeatherData';
import WeatherCard from './WeatherCard';
import { mockWeatherData } from '../testData';
import './WeatherDashboard.css';

const WeatherDashboard = () => {
  const { weatherData, loading, error } = useWeatherData();
  const [displayData, setDisplayData] = useState([]);

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
    return <div className="loading">Loading weather data...</div>;
  }

  return (
    <div className="weather-dashboard">
      <div className="weather-cards">
        {displayData.map((cityData) => (
          <WeatherCard key={cityData.RecNum} data={cityData} />
        ))}
      </div>
    </div>
  );
};

export default WeatherDashboard;