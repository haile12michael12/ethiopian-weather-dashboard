import { sql } from "drizzle-orm";
import { pgTable, text, varchar, integer, real, timestamp } from "drizzle-orm/pg-core";
import { createInsertSchema } from "drizzle-zod";
import { z } from "zod";

// Weather data schema
export const weatherData = pgTable("weather_data", {
  id: varchar("id").primaryKey().default(sql`gen_random_uuid()`),
  city: text("city").notNull(),
  date: text("date").notNull(),
  temperature: real("temperature").notNull(),
  minTemp: real("min_temp"),
  maxTemp: real("max_temp"),
  humidity: integer("humidity").notNull(),
  windSpeed: real("wind_speed").notNull(),
  pressure: integer("pressure").notNull(),
  visibility: real("visibility"),
  feelsLike: real("feels_like"),
  condition: text("condition").notNull(),
  timestamp: timestamp("timestamp").defaultNow(),
});

export const insertWeatherDataSchema = createInsertSchema(weatherData).omit({
  id: true,
  timestamp: true,
});

export type InsertWeatherData = z.infer<typeof insertWeatherDataSchema>;
export type WeatherData = typeof weatherData.$inferSelect;

// Users schema (keeping existing)
export const users = pgTable("users", {
  id: varchar("id").primaryKey().default(sql`gen_random_uuid()`),
  username: text("username").notNull().unique(),
  password: text("password").notNull(),
});

export const insertUserSchema = createInsertSchema(users).pick({
  username: true,
  password: true,
});

export type InsertUser = z.infer<typeof insertUserSchema>;
export type User = typeof users.$inferSelect;
