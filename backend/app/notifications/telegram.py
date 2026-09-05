"""
Telegram Bot Service and Broadcast Engine for Ethiopian Weather Alerts.
Provides:
- Interactive Bot commands: /start, /subscribe <city>, /unsubscribe, /forecast <city>, /alerts
- Automated emergency broadcasts when AlertLevel.CRITICAL triggers
- Daily morning forecast briefings
- Zero-token simulated dry-run mode for seamless local testing
"""
import os
import time
import logging
from typing import Dict, Any, List, Optional
import requests

from .storage import (
    save_telegram_subscription,
    remove_telegram_subscription,
    get_telegram_subscribers,
    is_alert_recently_sent,
    mark_alert_sent
)
from ..models import WeatherAlert, AlertLevel

logger = logging.getLogger(__name__)

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_API_BASE = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}" if TELEGRAM_BOT_TOKEN else None


def is_telegram_configured() -> bool:
    """Checks if a valid Telegram Bot token is present in the environment."""
    return bool(TELEGRAM_BOT_TOKEN and len(TELEGRAM_BOT_TOKEN) > 10)


def send_telegram_message(chat_id: int, text: str, parse_mode: str = "HTML") -> bool:
    """
    Sends a message to a Telegram chat.
    Operates in simulated dry-run mode if TELEGRAM_BOT_TOKEN is not configured.
    """
    if not is_telegram_configured():
        logger.info(f"[TELEGRAM DRY-RUN] Message to chat {chat_id}:\n{text}")
        return True

    url = f"{TELEGRAM_API_BASE}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": parse_mode,
        "disable_web_page_preview": True,
    }

    try:
        res = requests.post(url, json=payload, timeout=10)
        if res.status_code == 200:
            return True
        logger.warning(f"Telegram API responded with HTTP {res.status_code}: {res.text}")
        return False
    except Exception as exc:
        logger.error(f"Failed to send Telegram message to chat {chat_id}: {exc}")
        return False


def format_alert_message(alert: WeatherAlert) -> str:
    """Formats a WeatherAlert into an emergency Telegram message with safety instructions."""
    level_badge = "🚨 <b>CRITICAL EMERGENCY ALERT</b>" if alert.level == AlertLevel.CRITICAL else "⚠️ <b>WEATHER WARNING</b>"

    instructions = ""
    trigger = alert.trigger.lower()
    if "heat" in trigger:
        instructions = "• <i>Drink plenty of water and avoid direct midday solar exposure.\n• Shield livestock and working animals in shaded paddocks.</i>"
    elif "cold" in trigger or "frost" in trigger:
        instructions = "• <i>Dress in warm layers.\n• Highland farmers: initiate smoke smudging or furrow wetting to protect sensitive crops.</i>"
    elif "rain" in trigger or "flood" in trigger:
        instructions = "• <i>Stay away from active dry riverbeds (wadis) and rapid drainage channels.\n• Expect flash runoff in low-lying zones.</i>"
    elif "hazard" in trigger or "thunderstorm" in trigger:
        instructions = "• <i>Seek sturdy indoor shelter away from isolated trees or metallic structures.</i>"

    return (
        f"{level_badge}\n"
        f"📍 <b>City:</b> {alert.city_name}, Ethiopia\n"
        f"⚡ <b>Condition:</b> {alert.message}\n\n"
        f"<b>Safety Precautions:</b>\n"
        f"{instructions}\n\n"
        f"📡 <i>National Meteorology Agency & Live Dashboard</i>"
    )


def broadcast_telegram_alerts(alerts: List[WeatherAlert]) -> int:
    """
    Broadcasts critical and warning alerts to subscribed Telegram chats.
    Uses 12-hour deduplication to prevent repetitive notifications.
    Returns the number of messages successfully delivered.
    """
    delivered_count = 0

    for alert in alerts:
        # Only broadcast CRITICAL and WARNING alerts
        if alert.level not in (AlertLevel.CRITICAL, AlertLevel.WARNING):
            continue

        # Check deduplication log
        if is_alert_recently_sent(alert.city_name, alert.trigger, "telegram"):
            logger.info(f"Telegram alert for {alert.city_name} ({alert.trigger}) recently sent. Skipping.")
            continue

        # Get subscribers for this city + national subscribers
        subscribers = get_telegram_subscribers(alert.city_name)
        if not subscribers:
            continue

        message_text = format_alert_message(alert)

        for sub in subscribers:
            chat_id = sub["chat_id"]
            if send_telegram_message(chat_id, message_text):
                delivered_count += 1

        mark_alert_sent(alert.city_name, alert.trigger, "telegram")

    return delivered_count


# =========================================================================
# Interactive Bot Command Handling (Polling / Webhook)
# =========================================================================

def handle_telegram_command(chat_id: int, text: str, username: str = "") -> str:
    """Parses and handles Telegram commands like /start, /subscribe, /forecast, /alerts."""
    tokens = text.strip().split()
    cmd = tokens[0].lower() if tokens else ""
    args = tokens[1:]

    if cmd in ("/start", "/help"):
        return (
            "🇪🇹 <b>Ethiopian Weather Alert & Forecast Bot</b>\n\n"
            "ሰላም! Welcome to the official automated forecast service.\n\n"
            "<b>Available Commands:</b>\n"
            "• <code>/subscribe &lt;City&gt;</code> — Receive daily 7:00 AM weather briefs & severe weather alerts.\n"
            "  <i>Example: /subscribe Addis Ababa or /subscribe ALL</i>\n"
            "• <code>/unsubscribe</code> — Stop receiving alerts.\n"
            "• <code>/forecast &lt;City&gt;</code> — On-demand 3-day weather forecast.\n"
            "• <code>/alerts</code> — View active nationwide emergency alerts.\n"
            "• <code>/status</code> — Check your current subscription."
        )

    elif cmd == "/subscribe":
        if not args:
            return "⚠️ Please specify a city name.\n<i>Example:</i> <code>/subscribe Addis Ababa</code> or <code>/subscribe ALL</code>"
        city_name = " ".join(args).title()
        save_telegram_subscription(chat_id, city_name, username)
        return (
            f"✅ <b>Subscribed!</b>\n\n"
            f"You will receive daily 7:00 AM morning forecasts and instant emergency weather broadcasts for <b>{city_name}</b>.\n\n"
            f"To unsubscribe anytime, send <code>/unsubscribe</code>."
        )

    elif cmd == "/unsubscribe":
        remove_telegram_subscription(chat_id)
        return "👋 You have been unsubscribed from weather notifications."

    elif cmd == "/status":
        subs = get_telegram_subscribers()
        user_sub = next((s for s in subs if s["chat_id"] == chat_id), None)
        if user_sub:
            return f"🔔 <b>Active Subscription:</b> {user_sub['city_name']}\nChat ID: <code>{chat_id}</code>"
        return "ℹ️ You are not currently subscribed. Send <code>/subscribe &lt;City&gt;</code> to start."

    elif cmd == "/forecast":
        if not args:
            return "⚠️ Please provide a city name.\n<i>Example:</i> <code>/forecast Hawassa</code>"
        city_name = " ".join(args).title()

        # Fetch city forecast from DB
        from ..routes.forecast import get_city_forecast
        from fastapi import HTTPException
        try:
            fc = get_city_forecast(city_name)
            lines = [f"🌤️ <b>3-Day Forecast for {fc.name}</b> ({fc.region}):\n"]
            for d in fc.days:
                icon = "☀️" if "sun" in d.condition.lower() else "🌧️" if "rain" in d.condition.lower() else "⛅"
                lines.append(f"• <b>{d.label}</b>: {icon} {d.condition} | 🌡️ {d.max}°C / {d.min}°C | 💧 Rain: {d.rain_percent}%")
            lines.append(f"\n📡 <i>Source: {fc.data_source}</i>")
            return "\n".join(lines)
        except Exception:
            return f"❌ Could not retrieve forecast for '{city_name}'. Please verify the spelling."

    elif cmd == "/alerts":
        from ..database import get_connection, table_exists
        from ..routes.forecast import _build_city_forecast
        from ..alerts import detect_all_alerts

        if not table_exists():
            return "ℹ️ No weather data currently loaded."

        with get_connection() as conn:
            rows = conn.execute("""
                SELECT t.* FROM NMAthreedaysForcasetData t
                INNER JOIN (
                    SELECT City, MAX(RecNum) AS max_rec FROM NMAthreedaysForcasetData GROUP BY City
                ) latest ON t.City = latest.City AND t.RecNum = latest.max_rec
                ORDER BY t.City ASC
            """).fetchall()

        cities = [_build_city_forecast(dict(r)) for r in rows]
        active_alerts = detect_all_alerts(cities)

        if not active_alerts:
            return "☀️ <b>All Clear!</b> No extreme weather warnings currently active in Ethiopia."

        response_lines = [f"⚠️ <b>Active Weather Warnings ({len(active_alerts)}):</b>\n"]
        for a in active_alerts:
            icon = "🚨" if a.level == AlertLevel.CRITICAL else "⚠️"
            response_lines.append(f"{icon} <b>{a.city_name}</b>: {a.message}")

        return "\n".join(response_lines)

    return "Unknown command. Type <code>/help</code> for available options."


def run_telegram_polling():
    """Starts the long-polling event loop for the Telegram Bot."""
    if not is_telegram_configured():
        logger.warning("TELEGRAM_BOT_TOKEN is not set. Telegram bot polling cannot start live; operating in dry-run mode.")
        return

    logger.info("Starting Telegram Bot long-polling daemon...")
    offset = 0

    while True:
        try:
            url = f"{TELEGRAM_API_BASE}/getUpdates?offset={offset}&timeout=20"
            res = requests.get(url, timeout=25)
            if res.status_code != 200:
                time.sleep(5)
                continue

            data = res.json()
            for update in data.get("result", []):
                offset = update["update_id"] + 1
                msg = update.get("message", {})
                chat_id = msg.get("chat", {}).get("id")
                text = msg.get("text", "")
                username = msg.get("from", {}).get("username", "")

                if chat_id and text:
                    reply = handle_telegram_command(chat_id, text, username)
                    send_telegram_message(chat_id, reply)

        except Exception as exc:
            logger.error(f"Error in Telegram polling loop: {exc}")
            time.sleep(3)
