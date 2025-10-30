import { WeatherData } from './hooks/useWeatherData';

// Mock data for testing the frontend components
export const mockWeatherData: WeatherData[] = [
  {
    id: 1,
    city: "Addis Ababa",
    temperature: 20,
    humidity: 65,
    windSpeed: 12,
    pressure: 1013,
    uvIndex: 7,
    visibility: 10,
    weatherCondition: "Partly Cloudy",
    forecast: [
      {
        date: "2023-06-01",
        high: 25,
        low: 15,
        condition: "Sunny"
      },
      {
        date: "2023-06-02",
        high: 26,
        low: 16,
        condition: "Partly Cloudy"
      },
      {
        date: "2023-06-03",
        high: 24,
        low: 14,
        condition: "Rainy"
      }
    ]
  },
  {
    id: 2,
    city: "Dire Dawa",
    temperature: 26,
    humidity: 45,
    windSpeed: 8,
    pressure: 1010,
    uvIndex: 9,
    visibility: 15,
    weatherCondition: "Hot",
    forecast: [
      {
        date: "2023-06-01",
        high: 32,
        low: 20,
        condition: "Hot"
      },
      {
        date: "2023-06-02",
        high: 33,
        low: 21,
        condition: "Sunny"
      },
      {
        date: "2023-06-03",
        high: 31,
        low: 19,
        condition: "Partly Cloudy"
      }
    ]
  },
  {
    id: 3,
    city: "Mekelle",
    temperature: 17,
    humidity: 50,
    windSpeed: 15,
    pressure: 1008,
    uvIndex: 8,
    visibility: 12,
    weatherCondition: "Cloudy",
    forecast: [
      {
        date: "2023-06-01",
        high: 22,
        low: 12,
        condition: "Cloudy"
      },
      {
        date: "2023-06-02",
        high: 23,
        low: 13,
        condition: "Sunny"
      },
      {
        date: "2023-06-03",
        high: 21,
        low: 11,
        condition: "Windy"
      }
    ]
  }
];