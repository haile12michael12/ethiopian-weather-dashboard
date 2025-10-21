import { useState, useEffect } from 'react';
import { getAllWeatherData } from '../services/weatherService';

const useWeatherData = () => {
  const [weatherData, setWeatherData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchWeatherData = async () => {
      try {
        setLoading(true);
        setError(null);
        const response = await getAllWeatherData();
        
        if (response.success) {
          setWeatherData(response.data);
        } else {
          setError(response.error || 'Failed to fetch weather data');
        }
      } catch (err) {
        console.error('Error in useWeatherData hook:', err);
        setError('Failed to fetch weather data. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    fetchWeatherData();
  }, []);

  return { weatherData, loading, error };
};

export default useWeatherData;