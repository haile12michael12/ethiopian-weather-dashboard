import { Activity, BarChart3, Bell, CloudSun } from "lucide-react";
import NotificationBell from "./NotificationBell";

const links = [
  { href: "#overview", label: "Overview", icon: CloudSun },
  { href: "#forecast", label: "Forecast", icon: BarChart3 },
  { href: "#alerts", label: "Alerts", icon: Bell },
];

export default function Navbar({ isLive, dataSource, fallbackActive, cities = [] }) {
  const isFallback = fallbackActive || dataSource === "Open-Meteo";
  const statusLabel = !isLive
    ? "SAMPLE DATA"
    : isFallback
    ? "OPEN-METEO BACKUP"
    : "LIVE NMA";

  return (
    <nav className="top-nav" aria-label="Primary navigation">
      <a className="nav-brand" href="#overview" aria-label="Sky by sky home">
        <span className="nav-brand-mark"><CloudSun size={18} strokeWidth={2.2} /></span>
        <span className="sg">SKY BY SKY</span>
      </a>

      <div className="nav-links">
        {links.map(({ href, label, icon: Icon }) => (
          <a className="nav-link" href={href} key={href}>
            <Icon size={15} strokeWidth={2} />
            <span>{label}</span>
          </a>
        ))}
      </div>

      <div style={{ marginLeft: "auto", display: "flex", alignItems: "center", gap: 14 }}>
        <NotificationBell cities={cities} />

        <div
          className="nav-status"
          title={
            !isLive
              ? "Bundled sample data"
              : isFallback
              ? "Secondary fallback active via Open-Meteo ECMWF/GFS"
              : "Live feed from Ethiopia National Meteorology Agency"
          }
        >
          <Activity size={15} />
          <span>{statusLabel}</span>
          <span
            className={`status-dot ${isLive ? "is-live" : ""}`}
            style={isFallback ? { background: "#E8A33D", boxShadow: "0 0 0 3px rgba(232, 163, 61, 0.18)" } : {}}
          />
        </div>
      </div>
    </nav>
  );
}