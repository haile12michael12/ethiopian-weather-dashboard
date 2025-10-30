import { createContext, useContext, useState, useEffect } from "react";

type TemperatureUnit = "celsius" | "fahrenheit";

interface TemperatureContextType {
  unit: TemperatureUnit;
  toggleUnit: () => void;
  convertTemp: (celsius: number) => number;
  getUnitSymbol: () => string;
}

const TemperatureContext = createContext<TemperatureContextType | undefined>(undefined);

export function TemperatureProvider({ children }: { children: React.ReactNode }) {
  const [unit, setUnit] = useState<TemperatureUnit>(() => {
    const stored = localStorage.getItem("temperatureUnit");
    return (stored as TemperatureUnit) || "celsius";
  });

  useEffect(() => {
    localStorage.setItem("temperatureUnit", unit);
  }, [unit]);

  const toggleUnit = () => {
    setUnit((prev) => (prev === "celsius" ? "fahrenheit" : "celsius"));
  };

  const convertTemp = (celsius: number): number => {
    if (unit === "fahrenheit") {
      return (celsius * 9) / 5 + 32;
    }
    return celsius;
  };

  const getUnitSymbol = (): string => {
    return unit === "celsius" ? "°C" : "°F";
  };

  return (
    <TemperatureContext.Provider value={{ unit, toggleUnit, convertTemp, getUnitSymbol }}>
      {children}
    </TemperatureContext.Provider>
  );
}

export function useTemperature() {
  const context = useContext(TemperatureContext);
  if (!context) {
    throw new Error("useTemperature must be used within TemperatureProvider");
  }
  return context;
}
