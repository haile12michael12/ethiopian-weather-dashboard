import { Search, Layers } from "lucide-react";
import { motion } from "framer-motion";
import { COLORS } from "../theme";
import UnitToggle from "./UnitToggle";
import SortSelect from "./SortSelect";
import ExportButton from "./ExportButton";

export default function Controls({
  query, setQuery, region, setRegion, regions,
  unit, setUnit, sortBy, setSortBy,
  compareMode, setCompareMode, compareCount,
  exportCities,
}) {
  const regionVariants = {
    hidden: { opacity: 0, y: -10 },
    visible: (index) => ({
      opacity: 1,
      y: 0,
      transition: { delay: index * 0.05 },
    }),
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 12, marginBottom: 20 }}>
      <div style={{ display: "flex", flexWrap: "wrap", gap: 10, alignItems: "center" }}>
        <motion.div
          whileFocus={{ scale: 1.02 }}
          style={{
            display: "flex", alignItems: "center", gap: 8,
            background: COLORS.panelBg, border: `1px solid ${COLORS.panelBorder}`,
            borderRadius: 8, padding: "8px 12px", flex: "1 1 220px",
          }}
        >
          <Search size={15} color={COLORS.textMuted} />
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search a city..."
            style={{ background: "transparent", border: "none", outline: "none", color: COLORS.text, fontSize: 14, width: "100%" }}
          />
        </motion.div>

        <SortSelect sortBy={sortBy} setSortBy={setSortBy} />
        <UnitToggle unit={unit} setUnit={setUnit} />

        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={() => setCompareMode(!compareMode)}
          style={{
            display: "flex", alignItems: "center", gap: 6,
            background: compareMode ? COLORS.accent : "transparent",
            color: compareMode ? COLORS.accentText : COLORS.textMuted,
            border: `1px solid ${COLORS.panelBorder}`, borderRadius: 8,
            padding: "8px 12px", fontSize: 13, cursor: "pointer",
            fontWeight: compareMode ? 600 : 400,
          }}
        >
          <Layers size={14} />
          Compare{compareMode && compareCount ? ` (${compareCount})` : ""}
        </motion.button>

        <ExportButton cities={exportCities} />
      </div>

      <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
        {regions.map((r, index) => (
          <motion.button
            key={r}
            custom={index}
            variants={regionVariants}
            initial="hidden"
            animate="visible"
            whileHover={{ scale: 1.08 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => setRegion(r)}
            className="chip"
            style={{
              fontSize: 12.5, padding: "7px 12px", borderRadius: 999,
              border: `1px solid ${COLORS.panelBorder}`,
              background: region === r ? COLORS.accent : "transparent",
              color: region === r ? COLORS.accentText : "#CBD8D6",
              cursor: "pointer",
              fontWeight: region === r ? 600 : 400,
            }}
          >
            {r}
          </motion.button>
        ))}
      </div>
    </div>
  );
}
