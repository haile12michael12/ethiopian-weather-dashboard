import { COLORS } from "../theme";

export default function Header({ asOf, isLive }) {
  return (
    <div
      style={{
        display: "flex",
        justifyContent: "space-between",
        alignItems: "flex-end",
        flexWrap: "wrap",
        gap: 12,
        marginBottom: 28,
      }}
    >
      <div>
        <div className="sg" style={{ fontSize: 13, letterSpacing: "0.02em", color: COLORS.accent, marginBottom: 6 }}>
          National Meteorology Agency &middot; Three-Day Outlook
        </div>
        <h1 className="sg" style={{ fontSize: 32, fontWeight: 700, margin: 0, lineHeight: 1.1 }}>
          Ethiopia, sky by sky
        </h1>
      </div>
      <div style={{ fontSize: 13, color: COLORS.textMuted, textAlign: "right" }}>
        {isLive ? "As of" : ""} {asOf}
      </div>
    </div>
  );
}
