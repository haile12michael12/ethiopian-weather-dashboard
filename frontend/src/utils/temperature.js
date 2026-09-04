// Backend always sends Celsius (matches the NMA scraper's raw figures).
// These helpers convert for display only — never mutate the source data.

export function toDisplayTemp(celsius, unit) {
  if (unit === "F") return Math.round((celsius * 9) / 5 + 32);
  return celsius;
}

export function unitSuffix(unit) {
  return unit === "F" ? "\u00b0F" : "\u00b0C";
}
