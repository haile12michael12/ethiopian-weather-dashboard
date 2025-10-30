import { useState, useEffect } from "react";
import { Header } from "../components/Header";
import { CurrentWeather } from "../components/CurrentWeather";
import { StatsGrid } from "../components/StatsGrid";
import { WeatherChart } from "../components/WeatherChart";
import { MapView } from "../components/MapView";
import { Footer } from "../components/Footer";
import { ErrorState } from "../components/ErrorState";
import { EmptyState } from "../components/EmptyState";
import {
  CurrentWeatherSkeleton,
  StatsGridSkeleton,
  WeatherChartSkeleton,
} from "../components/SkeletonLoader";
import useWeatherData from "../hooks/useWeatherData";

export default function Dashboard() {
  const [searchQuery, setSearchQuery] = useState("");
  const { weatherData, loading, error } = useWeatherData();

  const filteredData = weatherData?.filter((item: any) =>
    item.city.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const currentWeather = filteredData?.[0];

  return (
    <div className="min-h-screen flex flex-col bg-background">
      <Header searchQuery={searchQuery} onSearchChange={setSearchQuery} />

      <main className="flex-1 container mx-auto px-4 py-6 md:py-8">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 md:gap-6 mb-6">
            {loading ? (
              <>
                <CurrentWeatherSkeleton />
                <StatsGridSkeleton />
              </>
            ) : error ? (
              <ErrorState
                message="Unable to fetch weather data. Please try again."
                onRetry={() => window.location.reload()}
              />
            ) : !filteredData || filteredData.length === 0 ? (
              searchQuery ? (
                <EmptyState searchQuery={searchQuery} />
              ) : (
                <ErrorState message="No weather data available." />
              )
            ) : (
              <>
                <CurrentWeather data={currentWeather!} />
                <div>
                  <StatsGrid data={currentWeather!} />
                </div>
              </>
            )}
          </div>

          {loading ? (
            <WeatherChartSkeleton />
          ) : filteredData && filteredData.length > 0 ? (
            <>
              <div className="mb-6">
                <WeatherChart data={filteredData} />
              </div>
              <MapView 
                weatherData={weatherData || []} 
                onCitySelect={(city) => setSearchQuery(city)}
              />
            </>
          ) : null}
        </div>
      </main>

      <Footer />
    </div>
  );
}