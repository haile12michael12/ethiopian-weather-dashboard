"""
Primary Weather Provider: National Meteorology Agency (NMA / EMI) Scraper.
Scrapes official Ethiopian 3-day meteorological forecasts from ethiomet.gov.et.
Includes retry logic, backoff, and raises NMAScraperError on failure to trigger fallbacks.
"""
import time
import logging
from typing import Dict, Any, List
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

NMA_FORECAST_URL = "http://www.ethiomet.gov.et/forecasts/three_day_forecast"
BACKUP_NMA_URL = "https://www.ethiomet.gov.et"


class NMAScraperError(Exception):
    """Raised when NMA scraping fails due to network, 404, or DOM structure changes."""
    pass


def fetch_nma_forecast(max_retries: int = 3, retry_delay: float = 2.0, timeout: int = 10) -> List[Dict[str, Any]]:
    """
    Attempts to scrape NMA forecast table with exponential backoff.
    Raises NMAScraperError if unreachable or table format has changed.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }

    last_error = None
    for attempt in range(1, max_retries + 1):
        try:
            logger.info(f"Connecting to NMA portal (attempt {attempt}/{max_retries})...")
            res = requests.get(NMA_FORECAST_URL, headers=headers, timeout=timeout)
            if res.status_code != 200:
                raise NMAScraperError(f"NMA server returned HTTP {res.status_code} on {NMA_FORECAST_URL}")

            soup = BeautifulSoup(res.text, "lxml" if "lxml" in BeautifulSoup.__module__ else "html.parser")
            table = soup.find("table")
            if not table:
                raise NMAScraperError("Could not locate forecast table in NMA HTML payload")

            # Parse table rows
            rows = table.find_all("tr")
            if len(rows) < 2:
                raise NMAScraperError("NMA table contains insufficient data rows")

            records: List[Dict[str, Any]] = []
            for tr in rows[1:]:
                cells = [td.get_text(strip=True) for td in tr.find_all(["td", "th"])]
                if len(cells) >= 10:
                    try:
                        record = {
                            "City": cells[1],
                            "MinTempD1": int(cells[2]),
                            "MaxTempD1": int(cells[3]),
                            "WeatherConditionD1": cells[4] or "Partly Cloudy",
                            "RainPercentD1": 0,
                            "WindD1": 0,
                            "MinTempD2": int(cells[5]),
                            "MaxTempD2": int(cells[6]),
                            "WeatherConditionD2": cells[7] or "Partly Cloudy",
                            "RainPercentD2": 0,
                            "WindD2": 0,
                            "MinTempD3": int(cells[8]),
                            "MaxTempD3": int(cells[9]),
                            "WeatherConditionD3": cells[10] if len(cells) > 10 else "Partly Cloudy",
                            "RainPercentD3": 0,
                            "WindD3": 0,
                            "DataSource": "NMA",
                        }
                        records.append(record)
                    except (ValueError, IndexError):
                        continue

            if not records:
                raise NMAScraperError("NMA table parsed, but zero valid city forecast records extracted")

            logger.info(f"Successfully scraped {len(records)} cities from NMA")
            return records

        except Exception as exc:
            last_error = exc
            logger.warning(f"NMA scrape attempt {attempt} failed: {exc}")
            if attempt < max_retries:
                time.sleep(retry_delay * attempt)

    raise NMAScraperError(f"NMA scraping exhausted {max_retries} attempts: {last_error}")
