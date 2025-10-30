import { motion } from "framer-motion";
import { Card } from "@/components/ui/card";
import { Droplets, Wind, Gauge, Thermometer, Eye } from "lucide-react";
import { useTemperature } from "@/contexts/TemperatureContext";
import type { WeatherData } from "@shared/schema";

interface StatsGridProps {
  data: WeatherData;
}

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
    },
  },
};

const itemVariants = {
  hidden: { y: 20, opacity: 0 },
  visible: {
    y: 0,
    opacity: 1,
    transition: {
      type: "spring",
      stiffness: 100,
    },
  },
};

export function StatsGrid({ data }: StatsGridProps) {
  const { convertTemp, getUnitSymbol } = useTemperature();
  
  const stats = [
    {
      label: "Humidity",
      value: `${data.humidity}%`,
      icon: <Droplets className="h-5 w-5 text-chart-1" />,
      testId: "text-humidity",
    },
    {
      label: "Wind Speed",
      value: `${data.windSpeed} km/h`,
      icon: <Wind className="h-5 w-5 text-chart-2" />,
      testId: "text-wind-speed",
    },
    {
      label: "Pressure",
      value: `${data.pressure} hPa`,
      icon: <Gauge className="h-5 w-5 text-chart-3" />,
      testId: "text-pressure",
    },
    {
      label: "Feels Like",
      value: data.feelsLike ? `${Math.round(convertTemp(data.feelsLike))}${getUnitSymbol()}` : "N/A",
      icon: <Thermometer className="h-5 w-5 text-chart-4" />,
      testId: "text-feels-like",
    },
    {
      label: "Visibility",
      value: data.visibility ? `${data.visibility} km` : "N/A",
      icon: <Eye className="h-5 w-5 text-chart-5" />,
      testId: "text-visibility",
    },
  ];

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-2 xl:grid-cols-3 gap-4"
    >
      {stats.map((stat, index) => (
        <motion.div key={stat.label} variants={itemVariants}>
          <Card className="p-4 border border-card-border hover-elevate transition-all duration-300">
            <div className="flex items-start justify-between gap-3">
              <div className="flex-1">
                <p className="text-xs text-muted-foreground mb-1">{stat.label}</p>
                <p className="text-xl font-bold text-foreground" data-testid={stat.testId}>
                  {stat.value}
                </p>
              </div>
              <div className="p-2 rounded-md bg-muted">{stat.icon}</div>
            </div>
          </Card>
        </motion.div>
      ))}
    </motion.div>
  );
}
