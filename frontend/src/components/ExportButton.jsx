import { Download } from "lucide-react";
import { COLORS } from "../theme";
import { downloadCSV } from "../utils/csv";

export default function ExportButton({ cities }) {
  return (
    <button
      onClick={() => downloadCSV(cities)}
      disabled={cities.length === 0}
      title="Download the current view as CSV"
      style={{
        display: "flex", alignItems: "center", gap: 6,
        background: "transparent", border: `1px solid ${COLORS.panelBorder}`,
        borderRadius: 8, padding: "8px 12px", fontSize: 13, cursor: cities.length ? "pointer" : "not-allowed",
        color: COLORS.textMuted, opacity: cities.length ? 1 : 0.5,
      }}
    >
      <Download size={14} />
      Export CSV
    </button>
  );
}
