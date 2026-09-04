import { SAMPLE_FORECAST } from "../data/sampleCities";

const BASE_URL = import.meta.env.VITE_API_BASE_URL || "";

// Falls back to bundled sample data if the API isn't reachable yet, so the
// UI is always usable (first deploy, backend down, offline dev).
export async function fetchForecast() {
  try {
    const res = await fetch(`${BASE_URL}/api/forecast`);
    if (!res.ok) throw new Error(`API responded ${res.status}`);
    const data = await res.json();
    return { data, isLive: true };
  } catch (err) {
    console.warn("Falling back to sample forecast data:", err.message);
    return { data: SAMPLE_FORECAST, isLive: false };
  }
}
