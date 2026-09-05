"""
Subscription and Notification Storage Layer.
Maintains persistent tables for Telegram Bot chats, Browser Web Push endpoints,
and a 12-hour alert deduplication log to prevent subscriber notification fatigue.
Compatible with both SQLite and PostgreSQL/TimescaleDB.
"""
import os
import time
import hashlib
import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, List, Optional
from ..database import get_connection, is_postgres

logger = logging.getLogger(__name__)


def init_notification_tables():
    """Initializes schema for telegram subscribers, webpush subscriptions, and alert logs."""
    with get_connection() as conn:
        if is_postgres():
            conn.execute("""
                CREATE TABLE IF NOT EXISTS telegram_subscriptions (
                    chat_id BIGINT PRIMARY KEY,
                    city_name VARCHAR(100) NOT NULL DEFAULT 'ALL',
                    username VARCHAR(100) DEFAULT '',
                    subscribed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    active BOOLEAN DEFAULT TRUE
                );
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS webpush_subscriptions (
                    endpoint TEXT PRIMARY KEY,
                    p256dh TEXT NOT NULL,
                    auth TEXT NOT NULL,
                    city_name VARCHAR(100) NOT NULL DEFAULT 'ALL',
                    subscribed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sent_alert_logs (
                    id VARCHAR(120) PRIMARY KEY,
                    alert_trigger VARCHAR(100) NOT NULL,
                    city_name VARCHAR(100) NOT NULL,
                    channel VARCHAR(50) NOT NULL,
                    sent_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """)
        else:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS telegram_subscriptions (
                    chat_id INTEGER PRIMARY KEY,
                    city_name TEXT NOT NULL DEFAULT 'ALL',
                    username TEXT DEFAULT '',
                    subscribed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    active INTEGER DEFAULT 1
                );
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS webpush_subscriptions (
                    endpoint TEXT PRIMARY KEY,
                    p256dh TEXT NOT NULL,
                    auth TEXT NOT NULL,
                    city_name TEXT NOT NULL DEFAULT 'ALL',
                    subscribed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sent_alert_logs (
                    id TEXT PRIMARY KEY,
                    alert_trigger TEXT NOT NULL,
                    city_name TEXT NOT NULL,
                    channel TEXT NOT NULL,
                    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
        conn.commit()


# =========================================================================
# Telegram Subscriptions
# =========================================================================

def save_telegram_subscription(chat_id: int, city_name: str = "ALL", username: str = "") -> bool:
    """Subscribes or updates a Telegram chat ID for a given city or all Ethiopia alerts."""
    init_notification_tables()
    city_clean = city_name.strip() if city_name else "ALL"
    with get_connection() as conn:
        if is_postgres():
            conn.execute("""
                INSERT INTO telegram_subscriptions (chat_id, city_name, username, active)
                VALUES (?, ?, ?, TRUE)
                ON CONFLICT (chat_id) DO UPDATE SET
                    city_name = EXCLUDED.city_name,
                    username = EXCLUDED.username,
                    active = TRUE,
                    subscribed_at = CURRENT_TIMESTAMP;
            """, (chat_id, city_clean, username))
        else:
            conn.execute("""
                INSERT INTO telegram_subscriptions (chat_id, city_name, username, active)
                VALUES (?, ?, ?, 1)
                ON CONFLICT (chat_id) DO UPDATE SET
                    city_name = excluded.city_name,
                    username = excluded.username,
                    active = 1,
                    subscribed_at = CURRENT_TIMESTAMP;
            """, (chat_id, city_clean, username))
        conn.commit()
    logger.info(f"Telegram subscription saved for chat {chat_id} (City: {city_clean})")
    return True


def remove_telegram_subscription(chat_id: int) -> bool:
    """Unsubscribes a Telegram chat."""
    init_notification_tables()
    with get_connection() as conn:
        conn.execute("UPDATE telegram_subscriptions SET active = 0 WHERE chat_id = ?;", (chat_id,))
        conn.commit()
    logger.info(f"Telegram chat {chat_id} unsubscribed.")
    return True


def get_telegram_subscribers(city_name: Optional[str] = None) -> List[Dict[str, Any]]:
    """Retrieves all active Telegram chat IDs subscribed to a city or to national alerts."""
    init_notification_tables()
    with get_connection() as conn:
        if city_name:
            rows = conn.execute("""
                SELECT chat_id, city_name, username
                FROM telegram_subscriptions
                WHERE (active = 1 OR active IS TRUE) AND (UPPER(city_name) = UPPER(?) OR UPPER(city_name) = 'ALL');
            """, (city_name,)).fetchall()
        else:
            rows = conn.execute("""
                SELECT chat_id, city_name, username
                FROM telegram_subscriptions
                WHERE active = 1 OR active IS TRUE;
            """).fetchall()

    return [dict(r) for r in rows]


# =========================================================================
# Web Push Subscriptions
# =========================================================================

def save_webpush_subscription(endpoint: str, p256dh: str, auth: str, city_name: str = "ALL") -> bool:
    """Saves or updates a Web Push browser subscription."""
    init_notification_tables()
    city_clean = city_name.strip() if city_name else "ALL"
    with get_connection() as conn:
        if is_postgres():
            conn.execute("""
                INSERT INTO webpush_subscriptions (endpoint, p256dh, auth, city_name)
                VALUES (?, ?, ?, ?)
                ON CONFLICT (endpoint) DO UPDATE SET
                    p256dh = EXCLUDED.p256dh,
                    auth = EXCLUDED.auth,
                    city_name = EXCLUDED.city_name,
                    subscribed_at = CURRENT_TIMESTAMP;
            """, (endpoint, p256dh, auth, city_clean))
        else:
            conn.execute("""
                INSERT INTO webpush_subscriptions (endpoint, p256dh, auth, city_name)
                VALUES (?, ?, ?, ?)
                ON CONFLICT (endpoint) DO UPDATE SET
                    p256dh = excluded.p256dh,
                    auth = excluded.auth,
                    city_name = excluded.city_name,
                    subscribed_at = CURRENT_TIMESTAMP;
            """, (endpoint, p256dh, auth, city_clean))
        conn.commit()
    logger.info(f"Web Push subscription registered (City: {city_clean})")
    return True


def remove_webpush_subscription(endpoint: str) -> bool:
    """Deletes a Web Push subscription endpoint (e.g. on user unsubscribe or HTTP 410 Gone)."""
    init_notification_tables()
    with get_connection() as conn:
        conn.execute("DELETE FROM webpush_subscriptions WHERE endpoint = ?;", (endpoint,))
        conn.commit()
    logger.info(f"Web Push subscription removed for endpoint.")
    return True


def get_webpush_subscribers(city_name: Optional[str] = None) -> List[Dict[str, Any]]:
    """Retrieves Web Push subscribers matching a city or subscribed to all alerts."""
    init_notification_tables()
    with get_connection() as conn:
        if city_name:
            rows = conn.execute("""
                SELECT endpoint, p256dh, auth, city_name
                FROM webpush_subscriptions
                WHERE UPPER(city_name) = UPPER(?) OR UPPER(city_name) = 'ALL';
            """, (city_name,)).fetchall()
        else:
            rows = conn.execute("""
                SELECT endpoint, p256dh, auth, city_name
                FROM webpush_subscriptions;
            """).fetchall()

    return [dict(r) for r in rows]


# =========================================================================
# Alert Deduplication (12-Hour Cooldown)
# =========================================================================

def _make_alert_key(city_name: str, trigger: str, channel: str) -> str:
    today_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    raw = f"{city_name.lower()}:{trigger.lower()}:{channel}:{today_date}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:32]


def is_alert_recently_sent(city_name: str, trigger: str, channel: str, cooldown_hours: int = 12) -> bool:
    """Checks if an alert for this city and trigger was already dispatched within cooldown_hours."""
    init_notification_tables()
    cutoff_iso = (datetime.now(timezone.utc) - timedelta(hours=cooldown_hours)).strftime("%Y-%m-%d %H:%M:%S")
    with get_connection() as conn:
        row = conn.execute("""
            SELECT 1 FROM sent_alert_logs
            WHERE LOWER(city_name) = LOWER(?) AND LOWER(alert_trigger) = LOWER(?) AND channel = ? AND sent_at >= ?
            LIMIT 1;
        """, (city_name, trigger, channel, cutoff_iso)).fetchone()
        return row is not None


def mark_alert_sent(city_name: str, trigger: str, channel: str) -> bool:
    """Records that an alert was dispatched to prevent redundant notifications."""
    init_notification_tables()
    log_id = _make_alert_key(city_name, trigger, channel)
    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    with get_connection() as conn:
        if is_postgres():
            conn.execute("""
                INSERT INTO sent_alert_logs (id, alert_trigger, city_name, channel, sent_at)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT (id) DO UPDATE SET sent_at = EXCLUDED.sent_at;
            """, (log_id, trigger, city_name, channel, now_iso))
        else:
            conn.execute("""
                INSERT INTO sent_alert_logs (id, alert_trigger, city_name, channel, sent_at)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT (id) DO UPDATE SET sent_at = excluded.sent_at;
            """, (log_id, trigger, city_name, channel, now_iso))
        conn.commit()
    return True


def get_notification_stats() -> Dict[str, Any]:
    """Returns telemetry on current subscriber counts and recent alerts dispatched."""
    init_notification_tables()
    cutoff_24h = (datetime.now(timezone.utc) - timedelta(hours=24)).strftime("%Y-%m-%d %H:%M:%S")
    with get_connection() as conn:
        t_count = conn.execute("SELECT COUNT(*) FROM telegram_subscriptions WHERE active = 1 OR active IS TRUE;").fetchone()
        w_count = conn.execute("SELECT COUNT(*) FROM webpush_subscriptions;").fetchone()
        a_count = conn.execute("SELECT COUNT(*) FROM sent_alert_logs WHERE sent_at >= ?;", (cutoff_24h,)).fetchone()

    return {
        "telegram_subscribers": t_count[0] if t_count else 0,
        "webpush_subscribers": w_count[0] if w_count else 0,
        "alerts_dispatched_last_24h": a_count[0] if a_count else 0,
    }
