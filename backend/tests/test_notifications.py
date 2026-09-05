"""
Unit and Integration Tests for Real-Time Automated Alert Dispatch (Telegram & Web Push).
Tests:
- Subscription persistence (Telegram & Web Push)
- 12-Hour alert deduplication to prevent alert fatigue
- Telegram command parsing & message formatting
- Web Push VAPID key generation and delivery mock
- FastAPI Notification routes (/api/notifications/*)
"""
import os
import sys
import pytest
from fastapi.testclient import TestClient

# Ensure backend root is on sys.path
TEST_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(TEST_DIR)
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from app.main import app
from app.models import WeatherAlert, AlertLevel
from app.notifications.storage import (
    save_telegram_subscription,
    remove_telegram_subscription,
    get_telegram_subscribers,
    save_webpush_subscription,
    remove_webpush_subscription,
    get_webpush_subscribers,
    is_alert_recently_sent,
    mark_alert_sent,
    get_notification_stats
)
from app.notifications.telegram import format_alert_message, handle_telegram_command
from app.notifications.webpush import get_public_vapid_key, broadcast_webpush_alerts


def test_telegram_subscription_lifecycle():
    """Test subscribing, querying, and unsubscribing a Telegram chat."""
    chat_id = 99887766
    city = "Dire Dawa"

    # Subscribe
    assert save_telegram_subscription(chat_id, city, username="test_user") is True

    # Query matching city
    subs = get_telegram_subscribers(city)
    matching = [s for s in subs if s["chat_id"] == chat_id]
    assert len(matching) == 1
    assert matching[0]["city_name"] == city

    # Unsubscribe
    assert remove_telegram_subscription(chat_id) is True
    subs_after = get_telegram_subscribers(city)
    matching_after = [s for s in subs_after if s["chat_id"] == chat_id]
    assert len(matching_after) == 0


def test_webpush_subscription_lifecycle():
    """Test saving, retrieving, and removing browser Web Push endpoints."""
    endpoint = "https://fcm.googleapis.com/fcm/send/test-device-token-12345"
    p256dh = "test-p256dh-key"
    auth = "test-auth-secret"
    city = "Semera"

    # Subscribe
    assert save_webpush_subscription(endpoint, p256dh, auth, city) is True

    # Query
    subs = get_webpush_subscribers(city)
    matching = [s for s in subs if s["endpoint"] == endpoint]
    assert len(matching) == 1
    assert matching[0]["p256dh"] == p256dh

    # Remove
    assert remove_webpush_subscription(endpoint) is True
    subs_after = get_webpush_subscribers(city)
    matching_after = [s for s in subs_after if s["endpoint"] == endpoint]
    assert len(matching_after) == 0


def test_alert_deduplication_cooldown():
    """Verify that alerts for the same city and trigger are deduplicated within cooldown window."""
    import time
    city = f"TestCity_{int(time.time() * 1000)}"
    trigger = "extreme_heat"
    channel = "telegram"

    # Initially not sent
    assert is_alert_recently_sent(city, trigger, channel) is False

    # Mark sent
    mark_alert_sent(city, trigger, channel)

    # Now should be detected as recently sent
    assert is_alert_recently_sent(city, trigger, channel) is True


def test_telegram_alert_message_formatting():
    """Verify emergency alert formatting contains required indicators and safety advice."""
    alert = WeatherAlert(
        city_name="Semera",
        level=AlertLevel.CRITICAL,
        message="Extreme heat warning: Temperature expected to reach 42°C",
        trigger="extreme_heat",
        value=42.0
    )
    formatted = format_alert_message(alert)
    assert "CRITICAL EMERGENCY ALERT" in formatted
    assert "Semera" in formatted
    assert "42°C" in formatted
    assert "Drink plenty of water" in formatted


def test_telegram_command_handling():
    """Test interactive bot command responses."""
    # /start
    start_reply = handle_telegram_command(12345, "/start")
    assert "Ethiopian Weather" in start_reply
    assert "/subscribe" in start_reply

    # /subscribe
    sub_reply = handle_telegram_command(12345, "/subscribe Hawassa", "ethio_farmer")
    assert "Subscribed!" in sub_reply
    assert "Hawassa" in sub_reply

    # /status
    status_reply = handle_telegram_command(12345, "/status")
    assert "Hawassa" in status_reply

    # /unsubscribe
    unsub_reply = handle_telegram_command(12345, "/unsubscribe")
    assert "unsubscribed" in unsub_reply


def test_vapid_key_endpoint():
    """Test GET /api/notifications/vapid-public-key returns valid key."""
    client = TestClient(app)
    res = client.get("/api/notifications/vapid-public-key")
    assert res.status_code == 200
    data = res.json()
    assert "public_key" in data
    assert len(data["public_key"]) > 20


def test_notification_api_endpoints():
    """Test subscribing and test dispatching via HTTP API."""
    client = TestClient(app)

    # Subscribe endpoint
    sub_payload = {
        "endpoint": "https://push.example.com/test-endpoint",
        "keys": {
            "p256dh": "mock-p256dh",
            "auth": "mock-auth"
        },
        "city_name": "Debre Birhan"
    }
    sub_res = client.post("/api/notifications/subscribe", json=sub_payload)
    assert sub_res.status_code == 200
    assert sub_res.json()["status"] == "subscribed"

    # Test alert endpoint
    test_payload = {
        "city_name": "Debre Birhan",
        "message": "Cold weather warning: 4°C expected",
        "level": "critical",
        "trigger": "extreme_cold"
    }
    test_res = client.post("/api/notifications/test", json=test_payload)
    assert test_res.status_code == 200
    assert test_res.json()["status"] == "dispatched"

    # Stats endpoint
    stats_res = client.get("/api/notifications/stats")
    assert stats_res.status_code == 200
    stats = stats_res.json()
    assert "telegram_subscribers" in stats
    assert "webpush_subscribers" in stats
