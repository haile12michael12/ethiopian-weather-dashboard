# Ethiopian Weather Dashboard

A React-based weather dashboard that displays three-day weather forecasts for major Ethiopian cities. The application scrapes data from the National Meteorology Agency of Ethiopia and presents it in an intuitive, responsive interface.

## Features

- Displays three-day weather forecasts for major Ethiopian cities
- Responsive design that works on desktop and mobile devices
- Clean, modern UI with weather icons
- Real-time data from National Meteorology Agency of Ethiopia

## Project Structure

```
ethiopian-weather-dashboard/
├── backend/
│   ├── NMA_web_Scrapping.py  # Web scraping script
│   ├── api.py                # Flask API server
│   └── requirements.txt      # Backend dependencies
├── frontend/
│   ├── src/
│   │   ├── components/       # React components
│   │   ├── hooks/            # Custom React hooks
│   │   ├── services/         # API service functions
│   │   ├── App.jsx           # Main App component
│   │   └── main.jsx          # Entry point
│   ├── index.html            # HTML template
│   └── package.json          # Frontend dependencies
└── README.md
```

## Prerequisites

- Python 3.7+
- Node.js 14+
- npm or yarn

## Setup Instructions

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   Or install them individually:
   ```bash
   pip install flask flask-cors
   ```

3. Run the web scraping script to collect weather data:
   ```bash
   python NMA_web_Scrapping.py
   ```

4. Start the Flask API server:
   ```bash
   python api.py
   ```
   The API will be available at `http://localhost:5000`

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```
   The frontend will be available at `http://localhost:5173`

## Usage

1. Ensure both the Flask backend (port 5000) and React frontend (port 5173) are running
2. Open your browser and navigate to `http://localhost:5173`
3. The dashboard will display the latest weather forecasts for Ethiopian cities

## API Endpoints

- `GET /api/weather` - Get all weather forecast data
- `GET /api/weather/<city>` - Get weather forecast data for a specific city
- `GET /health` - Health check endpoint

## Technologies Used

- **Frontend**: React, Vite, Axios
- **Backend**: Flask, SQLite, BeautifulSoup
- **Data Source**: National Meteorology Agency of Ethiopia (ethiomet.gov.et)

## Development

To build the frontend for production:
```bash
npm run build
```

To preview the production build:
```bash
npm run preview
```

## Testing the Application

Both the backend and frontend servers are now running:
- Backend API: http://localhost:5000
- Frontend Dashboard: http://localhost:5173

The dashboard displays weather forecast data for Ethiopian cities in a responsive grid layout with:
- City names
- Three-day forecasts with min/max temperatures
- Weather condition descriptions
- Visual weather icons

The application automatically fetches data from the backend API and displays it in an easy-to-read format.