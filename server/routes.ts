import type { Express } from "express";
import { createServer, type Server } from "http";
import { storage } from "./storage";

export async function registerRoutes(app: Express): Promise<Server> {
  app.get("/api/weather", async (req, res) => {
    try {
      const { city } = req.query;
      
      let weatherData;
      if (city && typeof city === "string") {
        weatherData = await storage.getWeatherByCity(city);
      } else {
        weatherData = await storage.getAllWeatherData();
      }
      
      res.json(weatherData);
    } catch (error) {
      console.error("Error fetching weather data:", error);
      res.status(500).json({ 
        error: "Failed to fetch weather data",
        message: error instanceof Error ? error.message : "Unknown error"
      });
    }
  });

  app.post("/api/weather", async (req, res) => {
    try {
      const { insertWeatherDataSchema } = await import("@shared/schema");
      const validationResult = insertWeatherDataSchema.safeParse(req.body);
      
      if (!validationResult.success) {
        return res.status(400).json({ 
          error: "Validation failed",
          details: validationResult.error.errors
        });
      }
      
      const weatherData = await storage.createWeatherData(validationResult.data);
      res.status(201).json(weatherData);
    } catch (error) {
      console.error("Error creating weather data:", error);
      res.status(500).json({ 
        error: "Failed to create weather data",
        message: error instanceof Error ? error.message : "Unknown error"
      });
    }
  });

  const httpServer = createServer(app);

  return httpServer;
}
