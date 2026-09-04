import { useState, useEffect } from "react";

// Small persisted-state hook. Falls back gracefully if localStorage is
// unavailable (private browsing, SSR, etc.) so it never breaks the app.
export function useLocalStorage(key, initialValue) {
  const [value, setValue] = useState(() => {
    try {
      const stored = window.localStorage.getItem(key);
      return stored !== null ? JSON.parse(stored) : initialValue;
    } catch {
      return initialValue;
    }
  });

  useEffect(() => {
    try {
      window.localStorage.setItem(key, JSON.stringify(value));
    } catch {
      // ignore write failures (storage full / disabled)
    }
  }, [key, value]);

  return [value, setValue];
}
