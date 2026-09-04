import { useState, useMemo, useEffect } from "react";
import Header from "./components/Header";
import HeroPanel from "./components/HeroPanel";
import Controls from "./components/Controls";
import CityGrid from "./components/CityGrid";
import AlertsBanner from "./components/AlertsBanner";
import { fetchForecast } from "./api/forecast";
import { useLocalStorage } from "./hooks/useLocalStorage";
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
      const matchesQuery = c.name.toLowerCase().includes(query.toLowerCase());
      const matchesRegion = region === "All regions" || c.region === region;
      return matchesQuery && matchesRegion;
    });
    return sortCities(matches, sortBy);
  }, [forecast, query, region, sortBy]);

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

  return (
    <div style={{ minHeight: "100%", padding: 0 }}>
      <div style={{ maxWidth: 1040, margin: "0 auto", padding: "40px 24px 64px" }}>
        <Header asOf={forecast.as_of} isLive={isLive} />

        <AlertsBanner cities={forecast.cities} unit={unit} onSelectCity={setSelectedId} />

        <HeroPanel city={hero} compareCities={compareMode ? compareCities : null} unit={unit} />

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

        {pinnedCities.length > 0 && (
          <div style={{ marginBottom: 20 }}>
            <div style={{ fontSize: 12.5, color: COLORS.textMuted, marginBottom: 8 }}>Pinned</div>
            <CityGrid
              cities={pinnedCities} selectedId={hero.id} onSelect={setSelectedId} query={query} region={region} unit={unit}
              pinnedIds={pinnedIds} onTogglePin={togglePin}
              compareMode={compareMode} compareIds={compareIds} onToggleCompare={toggleCompare}
            />
          </div>
        )}

        <CityGrid
          cities={restCities} selectedId={hero.id} onSelect={setSelectedId} query={query} region={region} unit={unit}
          pinnedIds={pinnedIds} onTogglePin={togglePin}
          compareMode={compareMode} compareIds={compareIds} onToggleCompare={toggleCompare}
        />

        <div style={{ marginTop: 36, paddingTop: 16, borderTop: `1px solid ${COLORS.panelBorder}`, fontSize: 12.5, color: COLORS.textSubtle }}>
          Source: {forecast.source}. {!isLive && "Showing bundled sample data — start the FastAPI backend to see live NMA figures."}
        </div>
      </div>
    </div>
  );
}
