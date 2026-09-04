import { Star, Check } from "lucide-react";
import ConditionIcon from "./ConditionIcon";
import { skyGradient } from "../theme";
import { toDisplayTemp, unitSuffix } from "../utils/temperature";

export default function CityCard({
  city, isActive, onSelect, unit,
  isPinned, onTogglePin,
  compareMode, isComparing, onToggleCompare,
}) {
  const today = city.days[0];
  const suffix = unitSuffix(unit);

  const handleClick = () => {
    if (compareMode) onToggleCompare(city.id);
    else onSelect(city.id);
  };

  return (
    <div
      className="card-btn"
      style={{
        position: "relative", borderRadius: 8, padding: 16,
        background: skyGradient(today.condition),
        border: isActive || isComparing ? "1px solid #E8A33D" : "1px solid transparent",
        color: "#F1EDE2",
      }}
    >
      <button
        onClick={(e) => { e.stopPropagation(); onTogglePin(city.id); }}
        title={isPinned ? "Unpin city" : "Pin city"}
        style={{
          position: "absolute", top: 10, right: 10, background: "transparent",
          border: "none", cursor: "pointer", padding: 2, lineHeight: 0,
        }}
      >
        <Star size={16} color="#E8A33D" fill={isPinned ? "#E8A33D" : "none"} />
      </button>

      <button onClick={handleClick} style={{ all: "unset", cursor: "pointer", display: "block", width: "100%" }}>
        {compareMode && (
          <div style={{
            display: "inline-flex", alignItems: "center", justifyContent: "center",
            width: 16, height: 16, borderRadius: 4, marginBottom: 8,
            border: "1px solid #E8A33D", background: isComparing ? "#E8A33D" : "transparent",
          }}>
            {isComparing && <Check size={12} color="#122024" />}
          </div>
        )}
        <div style={{ fontSize: 13, color: "#E6E0CF", marginBottom: 2, paddingRight: 20 }}>{city.region}</div>
        <div className="sg" style={{ fontSize: 17, fontWeight: 600, marginBottom: 10 }}>{city.name}</div>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
            <ConditionIcon condition={today.condition} size={18} />
            <span style={{ fontSize: 12.5 }}>{today.condition}</span>
          </div>
          <div className="sg" style={{ fontSize: 18, fontWeight: 600 }}>
            {toDisplayTemp(today.max, unit)}{suffix}
            <span style={{ fontSize: 13, fontWeight: 400, color: "#E6E0CF" }}>/{toDisplayTemp(today.min, unit)}{suffix}</span>
          </div>
        </div>
        <div style={{ display: "flex", gap: 10, marginTop: 12, paddingTop: 10, borderTop: "1px solid rgba(255,255,255,0.18)" }}>
          {city.days.slice(1).map((d, i) => (
            <div key={i} style={{ display: "flex", alignItems: "center", gap: 5, fontSize: 11.5, color: "#E6E0CF" }}>
              <ConditionIcon condition={d.condition} size={13} />
              {toDisplayTemp(d.max, unit)}{suffix}/{toDisplayTemp(d.min, unit)}{suffix}
            </div>
          ))}
        </div>
      </button>
    </div>
  );
}
