import { Activity, CloudSun } from "lucide-react";

const links = [
  { href: "#overview", label: "Overview" },
  { href: "#forecast", label: "Forecast" },
  { href: "#alerts", label: "Alerts" },
];

export default function Footer({ source, isLive }) {
  return (
    <footer className="site-footer">
      <div className="site-footer-inner">
        <a className="footer-brand" href="#overview" aria-label="Sky by sky home">
          <span className="footer-brand-mark"><CloudSun size={17} strokeWidth={2.2} /></span>
          <span className="sg">SKY BY SKY</span>
        </a>

        <nav className="footer-links" aria-label="Footer navigation">
          {links.map(({ href, label }) => (
            <a href={href} key={href}>{label}</a>
          ))}
        </nav>

        <div className="footer-meta">
          <span className="footer-source">
            <Activity size={14} />
            {isLive ? "Live NMA data" : "Sample forecast"}
          </span>
          <span className="footer-divider" aria-hidden="true" />
          <span>{source}</span>
          <span className="footer-divider" aria-hidden="true" />
          <span>{new Date().getFullYear()}</span>
        </div>
      </div>
    </footer>
  );
}
