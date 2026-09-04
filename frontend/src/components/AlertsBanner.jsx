import { CloudLightning, Thermometer } from "lucide-react";
import { COLORS, HEAT_ALERT_C, STORM_CONDITIONS } from "../theme";
import { toDisplayTemp, unitSuffix } from "../utils/temperature";

function cityAlerts(city) {
  const alerts = [];
  const hasStorm = city.days.some((d) => STORM_CONDITIONS.includes(d.condition));
  const hottest = Math.max(...city.days.map((d) => d.max));
  if (hasStorm) alerts.push("storm");
  if (hottest >= HEAT_ALERT_C) alerts.push("heat");
  return alerts;
}

export default function AlertsBanner({ cities, unit, onSelectCity }) {
  const flagged = cities
    .map((c) => ({ city: c, alerts: cityAlerts(c) }))
    .filter((x) => x.alerts.length > 0);

  if (flagged.length === 0) return null;

  return (
    <div
      style={{
        border: `1px solid rgba(232,163,61,0.4)`,
        background: "rgba(232,163,61,0.08)",
        borderRadius: 8,
        padding: "10px 14px",
        marginBottom: 20,
        display: "flex",
        flexWrap: "wrap",
        alignItems: "center",
        gap: 10,
      }}
    >
      <span style={{ fontSize: 12.5, color: COLORS.accent, fontWeight: 600, whiteSpace: "nowrap" }}>
        Watching {flagged.length} {flagged.length === 1 ? "city" : "cities"}
      </span>
      {flagged.map(({ city, alerts }) => {
        const hottest = Math.max(...city.days.map((d) => d.max));
        return (
          <button
            key={city.id}
            onClick={() => onSelectCity(city.id)}
            style={{
              display: "flex", alignItems: "center", gap: 6,
              background: "transparent", border: `1px solid ${COLORS.panelBorder}`,
              borderRadius: 999, padding: "5px 10px", cursor: "pointer",
              color: COLORS.text, fontSize: 12,
            }}
          >
            {alerts.includes("storm") && <CloudLightning size={13} color="#B7A7E5" />}
            {alerts.includes("heat") && <Thermometer size={13} color="#E27D60" />}
            {city.name}
            {alerts.includes("heat") && ` \u00b7 ${toDisplayTemp(hottest, unit)}${unitSuffix(unit)}`}
          </button>
        );
      })}
    </div>
  );
}
