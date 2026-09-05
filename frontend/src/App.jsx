import { useState, useMemo, useEffect } from "react";
import { motion } from "framer-motion";
import Header from "./components/Header";
import HeroPanel from "./components/HeroPanel";
import Controls from "./components/Controls";
import CityGrid from "./components/CityGrid";
import AlertsBanner from "./components/AlertsBanner";
import AdvancedChart from "./components/AdvancedChart";
import { fetchForecast } from "./api/forecast";
import { useLocalStorage } from "./hooks/useLocalStorage";
import { useDebounce } from "./hooks/useDebounce";
import { COLORS } from "./theme";

const MAX_COMPARE = 4;

function sortCities(cities, sortBy) {
  const sorted = [...cities];
  if (sortBy === "name") sorted.sort((a, b) => a.name.localeCompare(b.name));
  if (sortBy === "hottest") sorted.sort((a, b) => b.days[0].max - a.days[0].max);
  if (sortBy === "coldest") sorted.sort((a, b) => a.days[0].max - b.days[0].max);
  return sorted;
}

export default function App() {
  const [forecast, setForecast] = useState(null);
  const [isLive, setIsLive] = useState(false);
  const [selectedId, setSelectedId] = useState(null);
  const [query, setQuery] = useState("");
  const debouncedQuery = useDebounce(query, 300); // Debounce search with 300ms delay
  const [region, setRegion] = useState("All regions");
  const [sortBy, setSortBy] = useState("name");
  const [unit, setUnit] = useLocalStorage("nma-unit", "C");
  const [pinnedIds, setPinnedIds] = useLocalStorage("nma-pinned-cities", []);
  const [compareMode, setCompareMode] = useState(false);
  const [compareIds, setCompareIds] = useState([]);

  useEffect(() => {
    fetchForecast().then(({ data, isLive }) => {
      setForecast(data);
      setIsLive(isLive);
      setSelectedId(data.cities[0]?.id ?? null);
    });
  }, []);

  const regions = useMemo(() => {
    if (!forecast) return ["All regions"];
    return ["All regions", ...Array.from(new Set(forecast.cities.map((c) => c.region)))];
  }, [forecast]);

  const filtered = useMemo(() => {
    if (!forecast) return [];
    const matches = forecast.cities.filter((c) => {
      const matchesQuery = c.name.toLowerCase().includes(debouncedQuery.toLowerCase());
      const matchesRegion = region === "All regions" || c.region === region;
      return matchesQuery && matchesRegion;
    });
    return sortCities(matches, sortBy);
  }, [forecast, debouncedQuery, region, sortBy]);

  // Pinned cities always show first, in their own row, unaffected by sort.
  const pinnedCities = useMemo(
    () => (forecast ? forecast.cities.filter((c) => pinnedIds.includes(c.id)) : []),
    [forecast, pinnedIds]
  );
  const restCities = useMemo(
    () => filtered.filter((c) => !pinnedIds.includes(c.id)),
    [filtered, pinnedIds]
  );

  const togglePin = (id) => {
    setPinnedIds((prev) => (prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]));
  };

  const toggleCompare = (id) => {
    setCompareIds((prev) => {
      if (prev.includes(id)) return prev.filter((x) => x !== id);
      if (prev.length >= MAX_COMPARE) return prev;
      return [...prev, id];
    });
  };

  if (!forecast) {
    return (
      <div style={{ minHeight: "100%", display: "flex", alignItems: "center", justifyContent: "center", color: COLORS.textMuted }}>
        Loading forecast&hellip;
      </div>
    );
  }

  const hero = forecast.cities.find((c) => c.id === selectedId) || forecast.cities[0];
  const compareCities = forecast.cities.filter((c) => compareIds.includes(c.id));

  // Framer Motion variants
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
        delayChildren: 0.2,
      },
    },
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: { duration: 0.5, ease: "easeOut" },
    },
  };

  return (
    <motion.div
      initial="hidden"
      animate="visible"
      variants={containerVariants}
      style={{ minHeight: "100%", padding: 0 }}
    >
      <div style={{ maxWidth: 1040, margin: "0 auto", padding: "40px 24px 64px" }}>
        <motion.div variants={itemVariants}>
          <Header asOf={forecast.as_of} isLive={isLive} />
          <Header
            asOf={forecast.as_of}
            isLive={isLive}
            dataSource={forecast.data_source}
            fallbackActive={forecast.fallback_active}
            databaseType={forecast.database_type}
          />
        </motion.div>

        <motion.div variants={itemVariants}>
          <AlertsBanner cities={forecast.cities} unit={unit} onSelectCity={setSelectedId} />
        </motion.div>

        <motion.div variants={itemVariants}>
          <HeroPanel city={hero} compareCities={compareMode ? compareCities : null} unit={unit} />
        </motion.div>

        <motion.div variants={itemVariants}>
          <AdvancedChart city={hero} compareCities={compareMode ? compareCities : []} unit={unit} />
        </motion.div>

        <motion.div variants={itemVariants}>
          <Controls
            query={query} setQuery={setQuery}
            region={region} setRegion={setRegion} regions={regions}
            unit={unit} setUnit={setUnit}
            sortBy={sortBy} setSortBy={setSortBy}
            compareMode={compareMode}
            setCompareMode={(v) => { setCompareMode(v); if (!v) setCompareIds([]); }}
            compareCount={compareIds.length}
            exportCities={[...pinnedCities, ...restCities]}
          />
        </motion.div>

        {pinnedCities.length > 0 && (
          <motion.div variants={itemVariants} style={{ marginBottom: 20 }}>
            <div style={{ fontSize: 12.5, color: COLORS.textMuted, marginBottom: 8 }}>Pinned</div>
            <CityGrid
              cities={pinnedCities} selectedId={hero.id} onSelect={setSelectedId} query={query} region={region} unit={unit}
              pinnedIds={pinnedIds} onTogglePin={togglePin}
              compareMode={compareMode} compareIds={compareIds} onToggleCompare={toggleCompare}
            />
          </motion.div>
        )}

        <motion.div variants={itemVariants}>
          <CityGrid
            cities={restCities} selectedId={hero.id} onSelect={setSelectedId} query={query} region={region} unit={unit}
            pinnedIds={pinnedIds} onTogglePin={togglePin}
            compareMode={compareMode} compareIds={compareIds} onToggleCompare={toggleCompare}
          />
        </motion.div>

        <motion.div
          variants={itemVariants}
          style={{ marginTop: 36, paddingTop: 16, borderTop: `1px solid ${COLORS.panelBorder}`, fontSize: 12.5, color: COLORS.textSubtle }}
        >
          Source: {forecast.source}. {!isLive && "Showing bundled sample data — start the FastAPI backend to see live NMA figures."}
        </motion.div>
      </div>
    </motion.div>
  );
}
