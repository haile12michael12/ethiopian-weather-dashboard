import { MapPin } from "lucide-react";
import {
  ResponsiveContainer, LineChart, AreaChart, Area, Line, XAxis, YAxis, Tooltip, CartesianGrid, Legend,
} from "recharts";
import ConditionIcon from "./ConditionIcon";
import { COLORS, skyGradient, COMPARE_PALETTE } from "../theme";
import { toDisplayTemp, unitSuffix } from "../utils/temperature";

// Single-city hero: big current reading + high/low area trend.
function SingleCityHero({ city, unit }) {
  const today = city.days[0];
  const suffix = unitSuffix(unit);
  const trendData = city.days.map((d) => ({
    day: d.label, min: toDisplayTemp(d.min, unit), max: toDisplayTemp(d.max, unit),
  }));

  return (
    <div
      style={{
        background: skyGradient(today.condition), borderRadius: 10, padding: "28px 28px",
        display: "flex", flexWrap: "wrap", gap: 28, justifyContent: "space-between", alignItems: "center",
        border: "1px solid rgba(232,163,61,0.35)", marginBottom: 28,
      }}
    >
      <div style={{ minWidth: 220 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 6, fontSize: 13, color: "#E6E0CF", marginBottom: 6 }}>
          <MapPin size={14} />
          {city.name} &middot; {city.region}
        </div>
        <div style={{ display: "flex", alignItems: "baseline", gap: 10 }}>
          <span className="sg" style={{ fontSize: 64, fontWeight: 700, lineHeight: 1 }}>
            {toDisplayTemp(today.max, unit)}{suffix}
          </span>
          <span style={{ fontSize: 16, color: "#E6E0CF" }}>/ {toDisplayTemp(today.min, unit)}{suffix} low</span>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 8, marginTop: 8, fontSize: 15 }}>
          <ConditionIcon condition={today.condition} size={18} />
          {today.condition}
        </div>
      </div>

      <div style={{ flex: "1 1 320px", minWidth: 280, height: 140 }}>
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={trendData} margin={{ top: 10, right: 8, left: -20, bottom: 0 }}>
            <defs>
              <linearGradient id="maxFill" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor={COLORS.accent} stopOpacity={0.55} />
                <stop offset="100%" stopColor={COLORS.accent} stopOpacity={0.03} />
              </linearGradient>
            </defs>
            <CartesianGrid stroke="rgba(255,255,255,0.12)" vertical={false} />
            <XAxis dataKey="day" stroke="#E6E0CF" tickLine={false} axisLine={false} fontSize={12} />
            <YAxis stroke="#E6E0CF" tickLine={false} axisLine={false} fontSize={12} width={34} />
            <Tooltip contentStyle={{ background: COLORS.bg, border: `1px solid ${COLORS.accent}`, borderRadius: 6, fontSize: 12 }} labelStyle={{ color: COLORS.accent }} />
            <Area type="monotone" dataKey="max" stroke={COLORS.accent} fill="url(#maxFill)" strokeWidth={2} name="High" />
            <Area type="monotone" dataKey="min" stroke={COLORS.low} fill="transparent" strokeWidth={2} name="Low" />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

// Compare hero: overlays each selected city's daily high as its own line,
// so shapes/slopes across cities are easy to read side by side.
function CompareHero({ cities, unit }) {
  const suffix = unitSuffix(unit);
  const dayLabels = cities[0]?.days.map((d) => d.label) || [];
  const trendData = dayLabels.map((label, i) => {
    const row = { day: label };
    cities.forEach((c) => { row[c.name] = toDisplayTemp(c.days[i].max, unit); });
    return row;
  });

  return (
    <div
      style={{
        background: "linear-gradient(160deg, #1c2b3a 0%, #2f3f52 100%)",
        borderRadius: 10, padding: "24px 28px", border: "1px solid rgba(232,163,61,0.35)", marginBottom: 28,
      }}
    >
      <div style={{ fontSize: 13, color: "#E6E0CF", marginBottom: 14 }}>
        Comparing highs &middot; {cities.length} {cities.length === 1 ? "city" : "cities"} &middot; values in {suffix}
      </div>
      <div style={{ height: 220 }}>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={trendData} margin={{ top: 4, right: 12, left: -20, bottom: 0 }}>
            <CartesianGrid stroke="rgba(255,255,255,0.12)" vertical={false} />
            <XAxis dataKey="day" stroke="#E6E0CF" tickLine={false} axisLine={false} fontSize={12} />
            <YAxis stroke="#E6E0CF" tickLine={false} axisLine={false} fontSize={12} width={34} />
            <Tooltip contentStyle={{ background: COLORS.bg, border: `1px solid ${COLORS.accent}`, borderRadius: 6, fontSize: 12 }} labelStyle={{ color: COLORS.accent }} />
            <Legend wrapperStyle={{ fontSize: 12, color: "#E6E0CF" }} />
            {cities.map((c, i) => (
              <Line
                key={c.id}
                type="monotone"
                dataKey={c.name}
                stroke={COMPARE_PALETTE[i % COMPARE_PALETTE.length]}
                strokeWidth={2}
                dot={{ r: 3 }}
              />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

export default function HeroPanel({ city, compareCities, unit }) {
  if (compareCities && compareCities.length > 1) {
    return <CompareHero cities={compareCities} unit={unit} />;
  }
  return <SingleCityHero city={city} unit={unit} />;
}
