import { COLORS } from "../theme";

export default function Header({ asOf, isLive }) {
export default function Header({ asOf, isLive, dataSource, fallbackActive, databaseType }) {
  const isFallback = fallbackActive || dataSource === "Open-Meteo";

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
        <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 6 }}>
          <span className="sg" style={{ fontSize: 13, letterSpacing: "0.02em", color: COLORS.accent }}>
            National Meteorology Agency &middot; Three-Day Outlook
          </span>

          {/* Data Lineage & Resilience Badge */}
          {isLive ? (
            <span
              style={{
                display: "inline-flex",
                alignItems: "center",
                gap: 5,
                fontSize: 11,
                padding: "2px 8px",
                borderRadius: 999,
                fontWeight: 500,
                background: isFallback ? "rgba(232, 163, 61, 0.15)" : "rgba(78, 204, 163, 0.15)",
                color: isFallback ? "#E8A33D" : "#4ECCA3",
                border: `1px solid ${isFallback ? "rgba(232, 163, 61, 0.3)" : "rgba(78, 204, 163, 0.3)"}`,
              }}
              title={
                isFallback
                  ? "NMA portal unavailable. High-resolution ECMWF/GFS fallback active via Open-Meteo."
                  : "Direct feed from Ethiopia National Meteorology Agency."
              }
            >
              <span
                style={{
                  width: 6,
                  height: 6,
                  borderRadius: "50%",
                  backgroundColor: isFallback ? "#E8A33D" : "#4ECCA3",
                }}
              />
              {isFallback ? "Open-Meteo Backup" : "Official NMA"}
            </span>
          ) : (
            <span
              style={{
                fontSize: 11,
                padding: "2px 8px",
                borderRadius: 999,
                background: "rgba(155, 176, 174, 0.15)",
                color: COLORS.textMuted,
                border: "1px solid rgba(155, 176, 174, 0.25)",
              }}
            >
              Offline Sample
            </span>
          )}

          {databaseType && databaseType.includes("PostgreSQL") && (
            <span
              style={{
                fontSize: 11,
                padding: "2px 7px",
                borderRadius: 999,
                background: "rgba(51, 103, 145, 0.2)",
                color: "#8FD3C7",
                border: "1px solid rgba(143, 211, 199, 0.3)",
              }}
            >
              TimescaleDB
            </span>
          )}
        </div>

        <h1 className="sg" style={{ fontSize: 32, fontWeight: 700, margin: 0, lineHeight: 1.1 }}>
          Ethiopia, sky by sky
        </h1>
      </div>

      <div style={{ fontSize: 13, color: COLORS.textMuted, textAlign: "right" }}>
        {isLive ? "As of" : ""} {asOf}
        {isLive && asOf ? `Updated ${asOf}` : isLive ? "Live Feed" : "Bundled Data"}
      </div>
    </div>
  );
}
