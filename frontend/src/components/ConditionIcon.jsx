import { Sun, CloudSun, Cloud, CloudRain, CloudLightning, CloudDrizzle } from "lucide-react";

const ICONS = {
  Sunny: Sun,
  "Mostly Sunny": Sun,
  "Partly Cloudy": CloudSun,
  Cloudy: Cloud,
  "Rain Showers": CloudRain,
  "Scattered Showers": CloudDrizzle,
  Thunderstorms: CloudLightning,
};

export default function ConditionIcon({ condition, size = 18 }) {
  const Icon = ICONS[condition] || CloudSun;
  return <Icon size={size} />;
}
