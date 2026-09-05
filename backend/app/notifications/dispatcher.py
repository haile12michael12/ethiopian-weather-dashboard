"""
Central Alert Dispatcher.
Coordinates real-time emergency dispatch across Telegram and Browser Web Push channels.
Invoked automatically when the resilient ingestion pipeline completes.
"""
import logging
from typing import List, Dict, Any
from ..models import WeatherAlert, AlertLevel, CityForecast
from ..alerts import detect_all_alerts
from .telegram import broadcast_telegram_alerts
from .webpush import broadcast_webpush_alerts

logger = logging.getLogger(__name__)


def dispatch_alerts_for_cities(cities: List[CityForecast]) -> Dict[str, int]:
    """
    Evaluates weather alerts for all cities and triggers multi-channel broadcast.
    """
    all_alerts = detect_all_alerts(cities)
    critical_or_warning = [
        a for a in all_alerts
        if a.level in (AlertLevel.CRITICAL, AlertLevel.WARNING)
    ]

    if not critical_or_warning:
        logger.info("No critical or warning alerts detected in latest harvest.")
        return {"telegram": 0, "webpush": 0, "total_alerts": 0}

    logger.info(f"Dispatching notifications for {len(critical_or_warning)} active weather alerts...")

    telegram_sent = broadcast_telegram_alerts(critical_or_warning)
    webpush_sent = broadcast_webpush_alerts(critical_or_warning)

    logger.info(
        f"Alert dispatch summary: {telegram_sent} Telegram messages delivered, "
        f"{webpush_sent} Web Push notifications delivered."
    )

    return {
        "telegram": telegram_sent,
        "webpush": webpush_sent,
        "total_alerts": len(critical_or_warning)
    }
