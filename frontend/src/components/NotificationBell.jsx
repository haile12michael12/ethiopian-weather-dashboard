import { useState, useEffect } from "react";
import { Bell } from "lucide-react";
import { COLORS } from "../theme";
import { checkCurrentSubscription } from "../api/notifications";
import NotificationModal from "./NotificationModal";

export default function NotificationBell({ cities = [] }) {
  const [modalOpen, setModalOpen] = useState(false);
  const [isSubscribed, setIsSubscribed] = useState(false);

  useEffect(() => {
    checkCurrentSubscription().then((sub) => setIsSubscribed(!!sub));
  }, []);

  return (
    <>
      <button
        onClick={() => setModalOpen(true)}
        aria-label="Manage Weather Alerts"
        title="Real-Time Alerts (Telegram & Web Push)"
        style={{
          position: "relative",
          display: "inline-flex",
          alignItems: "center",
          gap: 6,
          background: isSubscribed ? "rgba(78, 204, 163, 0.12)" : "rgba(232, 163, 61, 0.12)",
          border: `1px solid ${isSubscribed ? "rgba(78, 204, 163, 0.3)" : "rgba(232, 163, 61, 0.3)"}`,
          borderRadius: 6,
          padding: "6px 10px",
          color: isSubscribed ? "#4ECCA3" : COLORS.accent,
          fontSize: 12,
          fontWeight: 500,
          cursor: "pointer",
          transition: "background 150ms ease, border-color 150ms ease",
        }}
      >
        <Bell size={14} />
        <span>Alerts</span>

        {/* Pulse dot indicator */}
        <span
          style={{
            position: "absolute",
            top: -3,
            right: -3,
            width: 7,
            height: 7,
            borderRadius: "50%",
            backgroundColor: isSubscribed ? "#4ECCA3" : COLORS.accent,
            boxShadow: `0 0 0 2px #122024`,
          }}
        />
      </button>

      <NotificationModal
        isOpen={modalOpen}
        onClose={() => {
          setModalOpen(false);
          checkCurrentSubscription().then((sub) => setIsSubscribed(!!sub));
        }}
        cities={cities}
      />
    </>
  );
}
