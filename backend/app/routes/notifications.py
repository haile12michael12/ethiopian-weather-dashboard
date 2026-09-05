"""
Web Push and Alert Notification API Routes.
Provides endpoints for registering browser push subscriptions, retrieving VAPID keys,
and triggering test emergency broadcasts.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

from ..notifications.webpush import (
    get_public_vapid_key,
    send_web_push,
    broadcast_webpush_alerts
)
from ..notifications.storage import (
    save_webpush_subscription,
    remove_webpush_subscription,
    get_notification_stats
)
from ..models import WeatherAlert, AlertLevel

router = APIRouter(prefix="/api/notifications", tags=["notifications"])


class WebPushKeys(BaseModel):
    p256dh: str
    auth: str


class WebPushSubscribeRequest(BaseModel):
    endpoint: str
    keys: WebPushKeys
    city_name: Optional[str] = "ALL"


class WebPushUnsubscribeRequest(BaseModel):
    endpoint: str


class TestAlertRequest(BaseModel):
    city_name: str = "Addis Ababa"
    message: str = "Test Emergency Weather Alert from Ethiopian Weather Dashboard"
    level: str = "critical"
    trigger: str = "test_broadcast"


@router.get("/vapid-public-key")
def get_vapid_key():
    """Returns the VAPID public key required by browser PushManager."""
    key = get_public_vapid_key()
    return {"public_key": key}


@router.post("/subscribe")
def subscribe_web_push(req: WebPushSubscribeRequest):
    """Registers a browser Web Push subscription."""
    success = save_webpush_subscription(
        endpoint=req.endpoint,
        p256dh=req.keys.p256dh,
        auth=req.keys.auth,
        city_name=req.city_name or "ALL"
    )
    return {"status": "subscribed", "city": req.city_name, "success": success}


@router.post("/unsubscribe")
def unsubscribe_web_push(req: WebPushUnsubscribeRequest):
    """Unregisters a browser Web Push subscription."""
    success = remove_webpush_subscription(req.endpoint)
    return {"status": "unsubscribed", "success": success}


@router.post("/test")
def send_test_notification(req: TestAlertRequest):
    """Dispatches a test emergency alert to all registered subscribers."""
    alert = WeatherAlert(
        city_name=req.city_name,
        level=AlertLevel.CRITICAL if req.level == "critical" else AlertLevel.WARNING,
        message=req.message,
        trigger=req.trigger,
        value=38.0
    )

    webpush_count = broadcast_webpush_alerts([alert])

    # Also test Telegram broadcast
    from ..notifications.telegram import broadcast_telegram_alerts
    telegram_count = broadcast_telegram_alerts([alert])

    return {
        "status": "dispatched",
        "alert": alert.model_dump(),
        "delivered": {
            "webpush": webpush_count,
            "telegram": telegram_count
        }
    }


@router.get("/stats")
def get_stats():
    """Returns active subscriber counts and notification metrics."""
    return get_notification_stats()
