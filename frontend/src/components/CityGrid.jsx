import { motion } from "framer-motion";
import CityCard from "./CityCard";
import { COLORS } from "../theme";

export default function CityGrid({
  cities, selectedId, onSelect, query, region, unit,
  pinnedIds, onTogglePin,
  compareMode, compareIds, onToggleCompare,
}) {
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.05,
        delayChildren: 0.1,
      },
    },
  };

  const itemVariants = {
    hidden: { opacity: 0, scale: 0.8 },
    visible: {
      opacity: 1,
      scale: 1,
      transition: { duration: 0.4 },
    },
  };

  if (cities.length === 0) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        style={{ textAlign: "center", color: COLORS.textMuted, padding: "40px 0", fontSize: 14 }}
      >
        No city matches "{query}" in {region}.
      </motion.div>
    );
  }

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(220px, 1fr))", gap: 12 }}
    >
      {cities.map((city) => (
        <motion.div key={city.id} variants={itemVariants}>
          <CityCard
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
        </motion.div>
      ))}
    </motion.div>
  );
}
