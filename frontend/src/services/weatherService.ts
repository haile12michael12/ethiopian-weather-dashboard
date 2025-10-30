import axios from 'axios';

// Define the weather data type
interface Forecast {
  date: string;
  high: number;
  low: number;
  condition: string;
}

interface WeatherData {
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

// For development, we'll use local JSON data
// In production, this would point to your backend API
const API_BASE_URL = '/weather-data.json';

// Create an axios instance with default configuration
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Function to get all weather data
export const getAllWeatherData = async (): Promise<WeatherData[]> => {
  try {
    // For development, we're using local JSON data
    const response = await fetch('/weather-data.json');
    const data: WeatherData[] = await response.json();
    return data;
    
    // For production with backend API, use this instead:
    // const response = await apiClient.get('');
    // return response.data;
  } catch (error) {
    console.error('Error fetching weather data:', error);
    throw error;
  }
};

// Function to get weather data for a specific city
export const getWeatherDataByCity = async (city: string): Promise<WeatherData | null> => {
  try {
    const allData = await getAllWeatherData();
    const cityData = allData.find(item => 
      item.city.toLowerCase() === city.toLowerCase()
    );
    return cityData || null;
  } catch (error) {
    console.error(`Error fetching weather data for ${city}:`, error);
    throw error;
  }
};

export default {
  getAllWeatherData,
  getWeatherDataByCity,
};