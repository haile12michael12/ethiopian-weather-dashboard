import { useState, useEffect } from "react";
import { Bell, Send, Check, X, ShieldAlert, Sparkles, Smartphone } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { COLORS } from "../theme";
import {
  subscribeToPush,
  unsubscribeFromPush,
  checkCurrentSubscription,
  sendTestNotification,
} from "../api/notifications";

export default function NotificationModal({ isOpen, onClose, cities = [] }) {
  const [isSubscribed, setIsSubscribed] = useState(false);
  const [selectedCity, setSelectedCity] = useState("ALL");
  const [loading, setLoading] = useState(false);
  const [statusMsg, setStatusMsg] = useState("");
  const [testSent, setTestSent] = useState(false);

  useEffect(() => {
    if (isOpen) {
      checkCurrentSubscription().then((subbed) => setIsSubscribed(!!subbed));
    }
  }, [isOpen]);

  const handleTogglePush = async () => {
    setLoading(true);
    setStatusMsg("");
    try {
      if (isSubscribed) {
        await unsubscribeFromPush();
        setIsSubscribed(false);
        setStatusMsg("Unsubscribed from browser notifications.");
      } else {
        await subscribeToPush(selectedCity);
        setIsSubscribed(true);
        setStatusMsg(`Subscribed to alerts for ${selectedCity === "ALL" ? "All Ethiopian Cities" : selectedCity}!`);
      }
    } catch (err) {
      setStatusMsg(`Error: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleTestNotification = async () => {
    setLoading(true);
    setTestSent(false);
    try {
      await sendTestNotification(selectedCity === "ALL" ? "Addis Ababa" : selectedCity);
      setTestSent(true);
      setStatusMsg("Test alert dispatched! Check your desktop/mobile notifications.");
    } catch (err) {
      setStatusMsg(`Test failed: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <div
        style={{
          position: "fixed",
          inset: 0,
          zIndex: 50,
          display: "grid",
          placeItems: "center",
          backgroundColor: "rgba(10, 18, 20, 0.8)",
          backdropFilter: "blur(8px)",
          padding: 16,
        }}
        onClick={onClose}
      >
        <motion.div
          initial={{ opacity: 0, scale: 0.95, y: 15 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95, y: 15 }}
          style={{
            width: "100%",
            maxWidth: 540,
            background: "#16262B",
            border: `1px solid ${COLORS.panelBorder}`,
            borderRadius: 12,
            boxShadow: "0 20px 40px rgba(0,0,0,0.5)",
            padding: 24,
            color: COLORS.text,
          }}
          onClick={(e) => e.stopPropagation()}
        >
          {/* Header */}
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 20 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
              <div
                style={{
                  width: 38,
                  height: 38,
                  borderRadius: 10,
                  backgroundColor: "rgba(232, 163, 61, 0.15)",
                  border: "1px solid rgba(232, 163, 61, 0.3)",
                  display: "grid",
                  placeItems: "center",
                  color: COLORS.accent,
                }}
              >
                <Bell size={20} />
              </div>
              <div>
                <h3 className="sg" style={{ margin: 0, fontSize: 18, fontWeight: 700 }}>
                  Real-Time Weather Alerts
                </h3>
                <span style={{ fontSize: 12.5, color: COLORS.textMuted }}>
                  Instant emergency dispatches & morning briefs
                </span>
              </div>
            </div>
            <button
              onClick={onClose}
              style={{
                background: "transparent",
                border: "none",
                color: COLORS.textMuted,
                cursor: "pointer",
                padding: 4,
              }}
            >
              <X size={18} />
            </button>
          </div>

          {/* Section 1: Browser Web Push */}
          <div
            style={{
              padding: 16,
              borderRadius: 8,
              background: "#122024",
              border: "1px solid rgba(255,255,255,0.06)",
              marginBottom: 16,
            }}
          >
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12 }}>
              <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                <ShieldAlert size={16} color={COLORS.accent} />
                <span style={{ fontSize: 14, fontWeight: 600 }}>Browser Push Notifications</span>
              </div>
              <span
                style={{
                  fontSize: 11,
                  padding: "3px 8px",
                  borderRadius: 999,
                  background: isSubscribed ? "rgba(78, 204, 163, 0.15)" : "rgba(155, 176, 174, 0.15)",
                  color: isSubscribed ? "#4ECCA3" : COLORS.textMuted,
                  border: `1px solid ${isSubscribed ? "rgba(78, 204, 163, 0.3)" : "rgba(155, 176, 174, 0.25)"}`,
                }}
              >
                {isSubscribed ? "Active" : "Not enabled"}
              </span>
            </div>

            <p style={{ fontSize: 12.5, color: COLORS.textMuted, margin: "0 0 14px 0", lineHeight: 1.4 }}>
              Receive system push banners on your desktop or Android device when hazardous thunderstorms, flash floods,
              or extreme heat (&gt;40°C) occur.
            </p>

            <div style={{ display: "flex", gap: 10, alignItems: "center", flexWrap: "wrap" }}>
              <select
                value={selectedCity}
                onChange={(e) => setSelectedCity(e.target.value)}
                style={{
                  flex: "1 1 180px",
                  padding: "8px 12px",
                  borderRadius: 6,
                  background: "#1B2C30",
                  border: `1px solid ${COLORS.panelBorder}`,
                  color: COLORS.text,
                  fontSize: 12.5,
                  outline: "none",
                }}
              >
                <option value="ALL">🇪🇹 All Ethiopia (Severe Alerts)</option>
                {cities.map((c) => (
                  <option key={c.id || c.name} value={c.name}>
                    {c.name} ({c.region})
                  </option>
                ))}
              </select>

              <button
                onClick={handleTogglePush}
                disabled={loading}
                style={{
                  padding: "8px 16px",
                  borderRadius: 6,
                  background: isSubscribed ? "#2C4147" : COLORS.accent,
                  color: isSubscribed ? COLORS.text : COLORS.accentText,
                  border: "none",
                  fontWeight: 600,
                  fontSize: 12.5,
                  cursor: "pointer",
                  display: "inline-flex",
                  alignItems: "center",
                  gap: 6,
                }}
              >
                {isSubscribed ? "Unsubscribe" : "Enable Push Alerts"}
              </button>

              {isSubscribed && (
                <button
                  onClick={handleTestNotification}
                  disabled={loading}
                  title="Send immediate test alert to this device"
                  style={{
                    padding: "8px 12px",
                    borderRadius: 6,
                    background: "transparent",
                    color: COLORS.accent,
                    border: `1px solid ${COLORS.accent}`,
                    fontSize: 12,
                    cursor: "pointer",
                    display: "inline-flex",
                    alignItems: "center",
                    gap: 5,
                  }}
                >
                  <Sparkles size={13} /> Test Notification
                </button>
              )}
            </div>

            {statusMsg && (
              <div style={{ marginTop: 10, fontSize: 12, color: statusMsg.startsWith("Error") ? "#E27D60" : "#4ECCA3" }}>
                {statusMsg}
              </div>
            )}
          </div>

          {/* Section 2: Telegram Bot */}
          <div
            style={{
              padding: 16,
              borderRadius: 8,
              background: "#122024",
              border: "1px solid rgba(255,255,255,0.06)",
            }}
          >
            <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 8 }}>
              <Smartphone size={16} color="#8FD3C7" />
              <span style={{ fontSize: 14, fontWeight: 600 }}>Telegram Alert Bot</span>
            </div>

            <p style={{ fontSize: 12.5, color: COLORS.textMuted, margin: "0 0 12px 0", lineHeight: 1.4 }}>
              Ethiopia’s most popular messenger. Get daily 7:00 AM briefs and instant emergency alerts directly in Telegram.
            </p>

            <div
              style={{
                background: "#1B2C30",
                padding: "10px 14px",
                borderRadius: 6,
                fontSize: 12,
                color: "#E6E0CF",
                display: "flex",
                flexDirection: "column",
                gap: 6,
                marginBottom: 12,
              }}
            >
              <div>
                • <code>/subscribe {selectedCity === "ALL" ? "Addis Ababa" : selectedCity}</code> — Daily briefs & emergency warnings
              </div>
              <div>
                • <code>/forecast {selectedCity === "ALL" ? "Hawassa" : selectedCity}</code> — On-demand 3-day forecast
              </div>
              <div>
                • <code>/alerts</code> — Active nationwide extreme weather warnings
              </div>
            </div>

            <a
              href="https://t.me"
              target="_blank"
              rel="noreferrer"
              style={{
                display: "inline-flex",
                alignItems: "center",
                gap: 7,
                padding: "8px 14px",
                borderRadius: 6,
                background: "#2Aabee",
                color: "#FFFFFF",
                textDecoration: "none",
                fontWeight: 600,
                fontSize: 12.5,
              }}
            >
              <Send size={14} /> Open Telegram Bot
            </a>
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  );
}
