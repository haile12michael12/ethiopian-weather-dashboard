import { type User, type InsertUser, type WeatherData, type InsertWeatherData } from "@shared/schema";
import { randomUUID } from "crypto";

export interface IStorage {
  getUser(id: string): Promise<User | undefined>;
  getUserByUsername(username: string): Promise<User | undefined>;
  createUser(user: InsertUser): Promise<User>;
  
  getAllWeatherData(): Promise<WeatherData[]>;
  getWeatherByCity(city: string): Promise<WeatherData[]>;
  createWeatherData(data: InsertWeatherData): Promise<WeatherData>;
}

export class MemStorage implements IStorage {
  private users: Map<string, User>;
  private weatherData: Map<string, WeatherData>;

  constructor() {
    this.users = new Map();
    this.weatherData = new Map();
    this.seedWeatherData();
  }

  private seedWeatherData() {
    const cities = [
      "Addis Ababa",
      "Dire Dawa", 
      "Mekele",
      "Gondar",
      "Bahir Dar",
      "Hawassa",
      "Jimma",
      "Dessie",
      "Adama",
      "Harar"
    ];

    const conditions = ["Sunny", "Partly Cloudy", "Cloudy", "Rainy", "Mostly Sunny"];
    
    const baseDate = new Date();
    
    cities.forEach((city, cityIndex) => {
      for (let i = 0; i < 7; i++) {
        const date = new Date(baseDate);
        date.setDate(date.getDate() - (6 - i));
        
        const baseTemp = 20 + cityIndex * 2 + Math.random() * 5;
        const variation = Math.sin(i / 2) * 3;
        const temperature = baseTemp + variation;
        
        const weatherEntry: WeatherData = {
          id: randomUUID(),
          city,
          date: date.toISOString().split('T')[0],
          temperature: Math.round(temperature * 10) / 10,
          minTemp: Math.round((temperature - 3) * 10) / 10,
          maxTemp: Math.round((temperature + 4) * 10) / 10,
          humidity: 50 + Math.floor(Math.random() * 30),
          windSpeed: Math.round((5 + Math.random() * 15) * 10) / 10,
          pressure: 1010 + Math.floor(Math.random() * 20),
          visibility: Math.round((8 + Math.random() * 4) * 10) / 10,
          feelsLike: Math.round((temperature + (Math.random() * 4 - 2)) * 10) / 10,
          condition: conditions[Math.floor(Math.random() * conditions.length)],
          timestamp: new Date() as any,
        };
        
        this.weatherData.set(weatherEntry.id, weatherEntry);
      }
    });
  }

  async getUser(id: string): Promise<User | undefined> {
    return this.users.get(id);
  }

  async getUserByUsername(username: string): Promise<User | undefined> {
    return Array.from(this.users.values()).find(
      (user) => user.username === username,
    );
  }

  async createUser(insertUser: InsertUser): Promise<User> {
    const id = randomUUID();
    const user: User = { ...insertUser, id };
    this.users.set(id, user);
    return user;
  }

  async getAllWeatherData(): Promise<WeatherData[]> {
    return Array.from(this.weatherData.values()).sort((a, b) => 
      new Date(b.date).getTime() - new Date(a.date).getTime()
    );
  }

  async getWeatherByCity(city: string): Promise<WeatherData[]> {
    return Array.from(this.weatherData.values())
      .filter((data) => data.city.toLowerCase() === city.toLowerCase())
      .sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime());
  }

  async createWeatherData(insertData: InsertWeatherData): Promise<WeatherData> {
    const id = randomUUID();
    const weatherEntry: WeatherData = {
      id,
      city: insertData.city,
      date: insertData.date,
      temperature: insertData.temperature,
      minTemp: insertData.minTemp ?? null,
      maxTemp: insertData.maxTemp ?? null,
      humidity: insertData.humidity,
      windSpeed: insertData.windSpeed,
      pressure: insertData.pressure,
      visibility: insertData.visibility ?? null,
      feelsLike: insertData.feelsLike ?? null,
      condition: insertData.condition,
      timestamp: new Date() as any,
    };
    this.weatherData.set(id, weatherEntry);
    return weatherEntry;
  }
}

export const storage = new MemStorage();
