# Ethiopian Weather Dashboard - Frontend

This is the frontend application for the Ethiopian Weather Dashboard, built with React, Vite, and Tailwind CSS.

## Features

- Weather dashboard for major Ethiopian cities
- 3-day weather forecasts
- Interactive map view
- Responsive design
- Dark mode support

## Pages

- **Dashboard**: Main weather dashboard showing current conditions and forecasts
- **About**: Information about Ethiopian climate zones and weather patterns

## Setup

1. Install dependencies:
   ```bash
   npm install
   ```

2. Start the development server:
   ```bash
   npm run dev
   ```

3. Build for production:
   ```bash
   npm run build
   ```

## Routing

This application uses `wouter` for client-side routing:

- `/` - Dashboard page
- `/about` - About page
- `/*` - 404 Not Found page

## API Integration

The frontend fetches weather data from a local JSON file during development. In a production environment, it would connect to the backend API.

## Technologies Used

- React
- Vite
- Tailwind CSS
- Wouter (routing)
- Axios (HTTP client)
- Recharts (data visualization)
- Leaflet (map visualization)
- Radix UI (UI components)