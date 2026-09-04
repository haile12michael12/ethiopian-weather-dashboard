import { COLORS } from "../theme";

export const SORT_OPTIONS = [
  { value: "name", label: "Name (A-Z)" },
  { value: "hottest", label: "Hottest first" },
  { value: "coldest", label: "Coldest first" },
];

export default function SortSelect({ sortBy, setSortBy }) {
  return (
    <select
      value={sortBy}
      onChange={(e) => setSortBy(e.target.value)}
      style={{
        background: COLORS.panelBg, color: COLORS.text,
        border: `1px solid ${COLORS.panelBorder}`, borderRadius: 8,
        padding: "8px 10px", fontSize: 13, cursor: "pointer",
      }}
    >
      {SORT_OPTIONS.map((opt) => (
        <option key={opt.value} value={opt.value}>{opt.label}</option>
      ))}
    </select>
  );
}
