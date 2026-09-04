import CityCard from "./CityCard";
import { COLORS } from "../theme";

export default function CityGrid({
  cities, selectedId, onSelect, query, region, unit,
  pinnedIds, onTogglePin,
  compareMode, compareIds, onToggleCompare,
}) {
  if (cities.length === 0) {
    return (
      <div style={{ textAlign: "center", color: COLORS.textMuted, padding: "40px 0", fontSize: 14 }}>
        No city matches "{query}" in {region}.
      </div>
    );
  }

  return (
    <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(220px, 1fr))", gap: 12 }}>
      {cities.map((city) => (
        <CityCard
          key={city.id}
          city={city}
          unit={unit}
          isActive={city.id === selectedId}
          onSelect={onSelect}
          isPinned={pinnedIds.includes(city.id)}
          onTogglePin={onTogglePin}
          compareMode={compareMode}
          isComparing={compareIds.includes(city.id)}
          onToggleCompare={onToggleCompare}
        />
      ))}
    </div>
  );
}
