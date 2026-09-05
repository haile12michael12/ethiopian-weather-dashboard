/**
 * API client for Browser Web Push and Telegram Alert notifications.
 */

const BASE_URL = import.meta.env.VITE_API_BASE_URL || "";

function urlBase64ToUint8Array(base64String) {
  const padding = "=".repeat((4 - (base64String.length % 4)) % 4);
  const base64 = (base64String + padding).replace(/\-/g, "+").replace(/_/g, "/");
  const rawData = window.atob(base64);
  const outputArray = new Uint8Array(rawData.length);
  for (let i = 0; i < rawData.length; ++i) {
    outputArray[i] = rawData.charCodeAt(i);
  }
  return outputArray;
}

export async function getVapidPublicKey() {
  try {
    const res = await fetch(`${BASE_URL}/api/notifications/vapid-public-key`);
    if (!res.ok) throw new Error("Failed to fetch VAPID key");
    const data = await res.json();
    return data.public_key;
  } catch (err) {
    console.warn("VAPID key unavailable:", err);
    return null;
  }
}

export async function subscribeToPush(cityName = "ALL") {
  if (!("serviceWorker" in navigator) || !("PushManager" in window)) {
    throw new Error("Web Push is not supported on this browser.");
  }

  const permission = await Notification.requestPermission();
  if (permission !== "granted") {
    throw new Error("Notification permission denied by user.");
  }

  const publicKey = await getVapidPublicKey();
  if (!publicKey) {
    throw new Error("Backend VAPID key is not configured yet.");
  }

  const registration = await navigator.serviceWorker.register("/sw.js");
  await navigator.serviceWorker.ready;

  let subscription = await registration.pushManager.getSubscription();
  if (!subscription) {
    const convertedKey = urlBase64ToUint8Array(publicKey);
    subscription = await registration.pushManager.subscribe({
      userVisibleOnly: true,
      applicationServerKey: convertedKey,
    });
  }

  const p256dh = btoa(String.fromCharCode.apply(null, new Uint8Array(subscription.getKey("p256dh"))));
  const auth = btoa(String.fromCharCode.apply(null, new Uint8Array(subscription.getKey("auth"))));

  const payload = {
    endpoint: subscription.endpoint,
    keys: { p256dh, auth },
    city_name: cityName,
  };

  const res = await fetch(`${BASE_URL}/api/notifications/subscribe`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!res.ok) throw new Error("Server failed to register subscription");
  return { success: true, city: cityName };
}

export async function unsubscribeFromPush() {
  if (!("serviceWorker" in navigator)) return false;

  const registration = await navigator.serviceWorker.ready;
  const subscription = await registration.pushManager.getSubscription();

  if (subscription) {
    await fetch(`${BASE_URL}/api/notifications/unsubscribe`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ endpoint: subscription.endpoint }),
    });
    await subscription.unsubscribe();
  }

  return true;
}

export async function checkCurrentSubscription() {
  if (!("serviceWorker" in navigator) || !("PushManager" in window)) return null;
  try {
    const registration = await navigator.serviceWorker.ready;
    const subscription = await registration.pushManager.getSubscription();
    return subscription !== null;
  } catch {
    return false;
  }
}

export async function sendTestNotification(cityName = "Addis Ababa") {
  const res = await fetch(`${BASE_URL}/api/notifications/test`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      city_name: cityName,
      message: `Emergency Alert Test: Heavy thunderstorm and lightning observed near ${cityName}.`,
      level: "critical",
      trigger: "test_broadcast",
    }),
  });
  return res.json();
}
