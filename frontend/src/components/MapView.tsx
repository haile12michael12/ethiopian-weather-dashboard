import { motion } from "framer-motion";
import { Card } from "@/components/ui/card";
import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import { Icon } from "leaflet";
import "leaflet/dist/leaflet.css";
import type { WeatherData } from "@shared/schema";
import { useTemperature } from "@/contexts/TemperatureContext";

interface MapViewProps {
  weatherData: WeatherData[];
  onCitySelect?: (city: string) => void;
}

const cityCoordinates: Record<string, [number, number]> = {
  "Addis Ababa": [9.0320, 38.7469],
  "Dire Dawa": [9.6011, 41.8661],
  "Mekele": [13.4967, 39.4753],
  "Gondar": [12.6000, 37.4667],
  "Bahir Dar": [11.5933, 37.3906],
  "Hawassa": [7.0625, 38.4769],
  "Jimma": [7.6733, 36.8344],
  "Dessie": [11.1333, 39.6333],
  "Adama": [8.5400, 39.2669],
  "Harar": [9.3100, 42.1367],
};

const createCustomIcon = (condition: string) => {
  const iconColor = condition === "Sunny" || condition === "Mostly Sunny" 
    ? "#f59e0b" 
    : condition.includes("Rain") 
    ? "#3b82f6" 
    : "#6b7280";
  
  return new Icon({
    iconUrl: `data:image/svg+xml;base64,${btoa(`
      <svg width="32" height="32" xmlns="http://www.w3.org/2000/svg">
        <circle cx="16" cy="16" r="12" fill="${iconColor}" stroke="white" stroke-width="2"/>
      </svg>
    `)}`,
    iconSize: [32, 32],
    iconAnchor: [16, 32],
    popupAnchor: [0, -32],
  });
};

export function MapView({ weatherData, onCitySelect }: MapViewProps) {
  const { convertTemp, getUnitSymbol } = useTemperature();
  
  const center: [number, number] = [9.145, 40.4897];

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, delay: 0.5 }}
    >
      <Card className="overflow-hidden">
        <div className="h-[400px] md:h-[500px] w-full">
          <MapContainer
            center={center}
            zoom={6}
            scrollWheelZoom={true}
            className="h-full w-full"
            data-testid="map-container"
          >
            <TileLayer
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />
            {weatherData.map((data) => {
              const coords = cityCoordinates[data.city];
              if (!coords) return null;

              return (
                <Marker
                  key={data.id}
                  position={coords}
                  icon={createCustomIcon(data.condition)}
                  eventHandlers={{
                    click: () => {
                      if (onCitySelect) {
                        onCitySelect(data.city);
                      }
                    },
                  }}
                >
                  <Popup>
                    <div className="p-2" data-testid={`popup-${data.city.toLowerCase().replace(/\s+/g, '-')}`}>
                      <h3 className="font-bold text-lg mb-2">{data.city}</h3>
                      <div className="space-y-1 text-sm">
                        <p>
                          <strong>Temperature:</strong> {Math.round(convertTemp(data.temperature))}{getUnitSymbol()}
                        </p>
                        <p>
                          <strong>Condition:</strong> {data.condition}
                        </p>
                        <p>
                          <strong>Humidity:</strong> {data.humidity}%
                        </p>
                        <p>
                          <strong>Wind:</strong> {data.windSpeed} km/h
                        </p>
                      </div>
                    </div>
                  </Popup>
                </Marker>
              );
            })}
          </MapContainer>
        </div>
      </Card>
    </motion.div>
  );
}
