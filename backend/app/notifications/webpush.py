"""
Browser Web Push Notification Service using W3C Push API and VAPID.
Generates/loads persistent VAPID keys, delivers encrypted push payloads,
and automatically prunes expired (HTTP 410 Gone) browser endpoints.
"""
import os
import json
import logging
from typing import Dict, Any, List, Optional
from pywebpush import webpush, WebPushException

from .storage import (
    save_webpush_subscription,
    remove_webpush_subscription,
    get_webpush_subscribers,
    is_alert_recently_sent,
    mark_alert_sent
)
from ..models import WeatherAlert, AlertLevel

logger = logging.getLogger(__name__)

VAPID_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vapid_keys.json")
VAPID_CLAIM_EMAIL = os.environ.get("VAPID_CLAIM_EMAIL", "mailto:alerts@ethiopianweather.org")


def get_or_create_vapid_keys() -> Dict[str, str]:
    """Retrieves or auto-generates persistent VAPID public/private keypair."""
    # Check environment first
    pub_env = os.environ.get("VAPID_PUBLIC_KEY")
    priv_env = os.environ.get("VAPID_PRIVATE_KEY")
    if pub_env and priv_env:
        return {"public_key": pub_env, "private_key": priv_env}

    # Check local JSON file
    if os.path.exists(VAPID_FILE):
        try:
            with open(VAPID_FILE, "r") as f:
                data = json.load(f)
                if "public_key" in data and "private_key" in data:
                    return data
        except Exception as e:
            logger.warning(f"Could not read existing VAPID keys file: {e}")

    # Generate new VAPID keypair using py_vapid
    from py_vapid import Vapid, b64urlencode
    from cryptography.hazmat.primitives import serialization

    vapid = Vapid()
    vapid.generate_keys()

    raw_pub = vapid.public_key.public_bytes(
        encoding=serialization.Encoding.X962,
        format=serialization.PublicFormat.UncompressedPoint
    )
    public_key_b64 = b64urlencode(raw_pub)
    private_pem_str = vapid.private_pem().decode("utf-8")

    keys = {
        "public_key": public_key_b64,
        "private_key": private_pem_str
    }

    try:
        with open(VAPID_FILE, "w") as f:
            json.dump(keys, f, indent=2)
        logger.info(f"Generated and saved fresh VAPID keypair to {VAPID_FILE}")
    except Exception as e:
        logger.warning(f"Could not save VAPID keys to file: {e}")

    return keys


def get_public_vapid_key() -> str:
    """Returns the application server public key for browser PushManager subscription."""
    return get_or_create_vapid_keys()["public_key"]


def send_web_push(subscription_info: Dict[str, Any], payload: Dict[str, Any]) -> bool:
    """
    Sends an encrypted Web Push notification to a browser endpoint.
    Automatically deletes subscription if endpoint has expired (HTTP 410 / 404).
    """
    keys = get_or_create_vapid_keys()
    endpoint = subscription_info.get("endpoint")

    try:
        webpush(
            subscription_info={
                "endpoint": endpoint,
                "keys": {
                    "p256dh": subscription_info.get("p256dh"),
                    "auth": subscription_info.get("auth")
                }
            },
            data=json.dumps(payload),
            vapid_private_key=keys["private_key"],
            vapid_claims={"sub": VAPID_CLAIM_EMAIL},
            timeout=8
        )
        return True
    except WebPushException as ex:
        # HTTP 404 / 410 indicates expired or revoked subscription
        if ex.response is not None and ex.response.status_code in (404, 410):
            logger.info(f"Purging expired Web Push endpoint: {endpoint}")
            remove_webpush_subscription(endpoint)
        else:
            logger.warning(f"Web Push delivery error: {ex}")
        return False
    except Exception as exc:
        err_msg = str(exc)
        if "deserialize key data" in err_msg or "padding" in err_msg.lower() or "asn.1" in err_msg.lower():
            logger.warning(f"Purging malformed/corrupted Web Push subscription: {endpoint}")
            remove_webpush_subscription(endpoint)
        else:
            logger.error(f"Unexpected Web Push failure: {exc}")
        return False


def broadcast_webpush_alerts(alerts: List[WeatherAlert]) -> int:
    """
    Delivers Web Push alerts for critical and warning conditions to subscribed browsers.
    Uses 12-hour deduplication to prevent spam.
    """
    delivered_count = 0

    for alert in alerts:
        if alert.level not in (AlertLevel.CRITICAL, AlertLevel.WARNING):
            continue

        if is_alert_recently_sent(alert.city_name, alert.trigger, "webpush"):
            logger.info(f"Web push alert for {alert.city_name} ({alert.trigger}) recently sent. Skipping.")
            continue

        subscribers = get_webpush_subscribers(alert.city_name)
        if not subscribers:
            continue

        payload = {
            "title": f"🚨 Weather Alert: {alert.city_name}" if alert.level == AlertLevel.CRITICAL else f"⚠️ Weather Warning: {alert.city_name}",
            "body": alert.message,
            "icon": "/logo192.png",
            "badge": "/badge72.png",
            "data": {
                "city": alert.city_name,
                "level": alert.level.value,
                "trigger": alert.trigger,
                "url": "/#alerts"
            }
        }

        for sub in subscribers:
            if send_web_push(sub, payload):
                delivered_count += 1

        mark_alert_sent(alert.city_name, alert.trigger, "webpush")

    return delivered_count
