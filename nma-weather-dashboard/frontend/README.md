# NMA Weather Dashboard — Frontend

React + Vite app for the "Ethiopia, sky by sky" three-day forecast dashboard.

## Setup

```bash
npm install
cp .env.example .env   # optionally set VITE_API_BASE_URL
npm run dev
```

Runs on http://localhost:5173. In dev, `/api` calls are proxied to
`http://localhost:8000` (see `vite.config.js`), so start the backend
(`../backend`) alongside it.

If the backend isn't reachable, the app falls back to bundled sample data
(`src/data/sampleCities.js`) so the UI still renders.

## Advanced features

- **°C / °F toggle** — persisted in `localStorage`, applies everywhere at once
- **Sort** — name, hottest first, coldest first
- **Pin cities** — star a city to keep it in its own "Pinned" row up top; persisted in `localStorage`
- **Compare mode** — select up to 4 cities and the hero panel swaps to an overlaid line chart of their highs across the 3 days
- **Alerts banner** — auto-flags any city forecasting thunderstorms or a high &ge; 36&deg;C, with a one-click jump to that city
- **CSV export** — downloads the currently filtered/sorted list of cities with their full 3-day figures

## Build

```bash
npm run build
npm run preview
```

## Structure

```
src/
├── App.jsx              # top-level state: forecast data, search, region filter, selected city
├── theme.js              # color tokens + sky-gradient-per-condition helper
├── api/forecast.js       # fetch wrapper with sample-data fallback
├── data/sampleCities.js  # fallback dataset, same shape as GET /api/forecast
└── components/
    ├── Header.jsx
    ├── HeroPanel.jsx      # featured city + 3-day min/max trend chart
    ├── Controls.jsx       # search box + region filter chips
    ├── CityGrid.jsx
    ├── CityCard.jsx
    └── ConditionIcon.jsx  # weather condition -> lucide icon
```
