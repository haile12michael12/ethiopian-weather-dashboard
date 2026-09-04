import { COLORS } from "../theme";

export default function UnitToggle({ unit, setUnit }) {
  return (
    <div style={{ display: "flex", border: `1px solid ${COLORS.panelBorder}`, borderRadius: 8, overflow: "hidden" }}>
      {["C", "F"].map((u) => (
        <button
          key={u}
          onClick={() => setUnit(u)}
          style={{
            padding: "8px 12px", fontSize: 13, cursor: "pointer", border: "none",
            background: unit === u ? COLORS.accent : "transparent",
            color: unit === u ? COLORS.accentText : COLORS.textMuted,
            fontWeight: unit === u ? 600 : 400,
          }}
        >
          &deg;{u}
        </button>
      ))}
    </div>
  );
}
