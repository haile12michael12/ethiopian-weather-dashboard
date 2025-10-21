import axios from 'axios';

const API_BASE_URL = '/api';

// Create an axios instance with default configuration
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Function to get all weather data
export const getAllWeatherData = async () => {
  try {
    const response = await apiClient.get('/weather');
    return response.data;
  } catch (error) {
    console.error('Error fetching weather data:', error);
    throw error;
  }
};

// Function to get weather data for a specific city
export const getWeatherDataByCity = async (city) => {
  try {
    const response = await apiClient.get(`/weather/${city}`);
    return response.data;
  } catch (error) {
    console.error(`Error fetching weather data for ${city}:`, error);
    throw error;
  }
};

export default {
  getAllWeatherData,
  getWeatherDataByCity,
};