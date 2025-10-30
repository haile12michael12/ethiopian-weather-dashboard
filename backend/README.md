# Ethiopian Weather Dashboard Backend

This is the backend component of the Ethiopian Weather Dashboard application. It provides a REST API for accessing weather forecast data for major Ethiopian cities.

## Project Structure

```
backend/
├── app.py                 # Main Flask application
├── NMA_web_Scrapping.py   # Web scraping script
├── create_test_db.py      # Test database creation script
├── requirements.txt       # Python dependencies
├── controllers/           # API controllers
│   ├── __init__.py
│   └── weather_controller.py
├── models/                # Data models
│   ├── __init__.py
│   └── weather_model.py
├── services/              # Business logic
│   ├── __init__.py
│   └── weather_service.py
├── utils/                 # Utility functions
│   ├── __init__.py
│   └── config.py
└── README.md             # This file
```

## Components

### Controllers
Handle HTTP requests and responses. They interact with services to process business logic.

### Services
Contain the business logic of the application. They interact with models to access data.

### Models
Handle data access and database operations.

### Utilities
Provide common utility functions used across the application.

## API Endpoints

- `GET /api/weather` - Get all weather forecast data
- `GET /api/weather/<city>` - Get weather forecast data for a specific city
- `GET /health` - Health check endpoint

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the web scraping script to collect weather data:
   ```bash
   python NMA_web_Scrapping.py
   ```

3. Start the Flask server:
   ```bash
   python app.py
   ```

The API will be available at `http://localhost:5000`.