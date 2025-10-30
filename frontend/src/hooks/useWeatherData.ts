import { useState, useEffect } from 'react';
import { getAllWeatherData } from '../services/weatherService';

interface Forecast {
  date: string;
  high: number;
  low: number;
  condition: string;
}

export interface WeatherData {
  id: number;
  city: string;
  temperature: number;
  humidity: number;
  windSpeed: number;
  pressure: number;
  uvIndex: number;
  visibility: number;
  weatherCondition: string;
  forecast: Forecast[];
}

interface UseWeatherDataReturn {
  weatherData: WeatherData[];
  loading: boolean;
  error: string | null;
}

const useWeatherData = (): UseWeatherDataReturn => {
  const [weatherData, setWeatherData] = useState<WeatherData[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchWeatherData = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await getAllWeatherData();
        setWeatherData(data);
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