// Shared design tokens for the "sky by sky" theme.

export const COLORS = {
  bg: "#122024",
  panelBorder: "#2C4147",
  panelBg: "#1B2C30",
  text: "#F1EDE2",
  textMuted: "#9BB0AE",
  textSubtle: "#7F9694",
  accent: "#E8A33D",
  accentText: "#122024",
  low: "#8FD3C7",
};

export const SKY_GRADIENTS = {
  Sunny: "linear-gradient(160deg, #2f6b8f 0%, #e8a33d 100%)",
  "Mostly Sunny": "linear-gradient(160deg, #2c5f82 0%, #d9974a 100%)",
  "Partly Cloudy": "linear-gradient(160deg, #35566b 0%, #7c93a0 100%)",
  Cloudy: "linear-gradient(160deg, #33414a 0%, #5c6b73 100%)",
  "Rain Showers": "linear-gradient(160deg, #1c2b3a 0%, #3d5566 100%)",
  "Scattered Showers": "linear-gradient(160deg, #223447 0%, #47657a 100%)",
  Thunderstorms: "linear-gradient(160deg, #10161f 0%, #33293f 100%)",
};

export function skyGradient(condition) {
  return SKY_GRADIENTS[condition] || SKY_GRADIENTS["Partly Cloudy"];
}

// Distinct line colors for compare mode, chosen to stay legible against
// the dark hero panel background.
export const COMPARE_PALETTE = ["#E8A33D", "#8FD3C7", "#E27D60", "#B7A7E5", "#8CC24A"];

// Thresholds that drive the alerts banner.
export const HEAT_ALERT_C = 36;
export const STORM_CONDITIONS = ["Thunderstorms"];
