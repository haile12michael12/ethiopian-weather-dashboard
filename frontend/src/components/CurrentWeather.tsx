import { motion, useMotionValue, useTransform, animate } from "framer-motion";
import { useEffect } from "react";
import { Card } from "@/components/ui/card";
import { Cloud, CloudRain, Sun, CloudDrizzle, CloudSnow } from "lucide-react";
import { useTemperature } from "@/contexts/TemperatureContext";
import type { WeatherData } from "@shared/schema";

interface CurrentWeatherProps {
  data: WeatherData;
}

const conditionIcons: Record<string, React.ReactNode> = {
  Sunny: <Sun className="h-20 w-20 md:h-24 md:w-24 text-chart-2" />,
  "Mostly Sunny": <Sun className="h-20 w-20 md:h-24 md:w-24 text-chart-2" />,
  Clear: <Sun className="h-20 w-20 md:h-24 md:w-24 text-chart-2" />,
  Cloudy: <Cloud className="h-20 w-20 md:h-24 md:w-24 text-muted-foreground" />,
  "Partly Cloudy": <Cloud className="h-20 w-20 md:h-24 md:w-24 text-muted-foreground" />,
  Rainy: <CloudRain className="h-20 w-20 md:h-24 md:w-24 text-chart-1" />,
  Rain: <CloudRain className="h-20 w-20 md:h-24 md:w-24 text-chart-1" />,
  Drizzle: <CloudDrizzle className="h-20 w-20 md:h-24 md:w-24 text-chart-1" />,
  Snow: <CloudSnow className="h-20 w-20 md:h-24 md:w-24 text-chart-1" />,
};

const getConditionGradient = (condition: string) => {
  const lower = condition.toLowerCase();
  if (lower.includes("sunny") || lower.includes("clear")) {
    return "from-amber-400/20 via-orange-300/20 to-yellow-400/20";
  }
  if (lower.includes("rain") || lower.includes("drizzle")) {
    return "from-blue-400/20 via-cyan-300/20 to-blue-500/20";
  }
  if (lower.includes("snow")) {
    return "from-blue-200/20 via-cyan-100/20 to-slate-300/20";
  }
  return "from-slate-400/20 via-gray-300/20 to-slate-400/20";
};

function AnimatedTemperature({ value }: { value: number }) {
  const count = useMotionValue(0);
  const rounded = useTransform(count, (latest) => Math.round(latest));

  useEffect(() => {
    const controls = animate(count, value, { duration: 1, ease: "easeOut" });
    return controls.stop;
  }, [value, count]);

  return <motion.span>{rounded}</motion.span>;
}

export function CurrentWeather({ data }: CurrentWeatherProps) {
  const { convertTemp, getUnitSymbol } = useTemperature();
  const icon = conditionIcons[data.condition] || conditionIcons.Cloudy;
  const gradientClass = getConditionGradient(data.condition);

  const displayTemp = Math.round(convertTemp(data.temperature));
  const displayFeelsLike = data.feelsLike ? Math.round(convertTemp(data.feelsLike)) : null;
  const displayMin = data.minTemp ? Math.round(convertTemp(data.minTemp)) : null;
  const displayMax = data.maxTemp ? Math.round(convertTemp(data.maxTemp)) : null;
  const unitSymbol = getUnitSymbol();

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, delay: 0.1 }}
      className="col-span-1 md:col-span-2"
    >
      <Card className={`p-6 md:p-8 border border-card-border bg-gradient-to-br ${gradientClass} backdrop-blur-sm relative overflow-hidden`}>
        <div className="absolute inset-0 bg-card/90 backdrop-blur-sm"></div>
        <div className="relative z-10">
          <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
            <div className="flex-1">
              <motion.h2
                initial={{ x: -20, opacity: 0 }}
                animate={{ x: 0, opacity: 1 }}
                transition={{ delay: 0.2 }}
                className="text-2xl md:text-3xl font-bold text-foreground"
                data-testid="text-city-name"
              >
                {data.city}
              </motion.h2>
              <motion.p
                initial={{ x: -20, opacity: 0 }}
                animate={{ x: 0, opacity: 1 }}
                transition={{ delay: 0.3 }}
                className="text-sm text-muted-foreground mt-1"
              >
                {new Date(data.date).toLocaleDateString("en-US", {
                  weekday: "long",
                  year: "numeric",
                  month: "long",
                  day: "numeric",
                })}
              </motion.p>

              <motion.div
                initial={{ scale: 0.8, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{ delay: 0.4, type: "spring" }}
                className="mt-6"
              >
                <div className="flex items-baseline gap-2">
                  <span className="text-6xl md:text-7xl font-bold text-foreground" data-testid="text-temperature">
                    <AnimatedTemperature value={displayTemp} />
                  </span>
                  <span className="text-4xl md:text-5xl font-semibold text-muted-foreground">{unitSymbol}</span>
                </div>
                <p className="text-lg md:text-xl text-muted-foreground mt-2" data-testid="text-condition">
                  {data.condition}
                </p>
                {displayFeelsLike !== null && (
                  <p className="text-sm text-muted-foreground mt-1">
                    Feels like {displayFeelsLike}{unitSymbol}
                  </p>
                )}
              </motion.div>
            </div>

            <motion.div
              initial={{ scale: 0, rotate: -180 }}
              animate={{ scale: 1, rotate: 0 }}
              transition={{ delay: 0.5, type: "spring", stiffness: 200 }}
              className="flex items-center justify-center"
            >
              {icon}
            </motion.div>
          </div>

          {displayMin !== null && displayMax !== null && (
            <motion.div
              initial={{ y: 20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ delay: 0.6 }}
              className="mt-6 flex gap-4"
            >
              <div className="flex items-center gap-2">
                <span className="text-sm text-muted-foreground">Min:</span>
                <span className="text-lg font-semibold text-foreground">{displayMin}{unitSymbol}</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-sm text-muted-foreground">Max:</span>
                <span className="text-lg font-semibold text-foreground">{displayMax}{unitSymbol}</span>
              </div>
            </motion.div>
          )}
        </div>
      </Card>
    </motion.div>
  );
}
