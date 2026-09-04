// Client-side CSV export — no backend round trip needed since the data
// is already in memory.

export function citiesToCSV(cities) {
  const header = [
    "City", "Region",
    "MinTempD1", "MaxTempD1", "ConditionD1",
    "MinTempD2", "MaxTempD2", "ConditionD2",
    "MinTempD3", "MaxTempD3", "ConditionD3",
  ];
  const rows = cities.map((c) => [
    c.name, c.region,
    ...c.days.flatMap((d) => [d.min, d.max, d.condition]),
  ]);
  const escape = (v) => (typeof v === "string" && v.includes(",") ? `"${v}"` : v);
  return [header, ...rows].map((r) => r.map(escape).join(",")).join("\n");
}

export function downloadCSV(cities, filename = "nma-forecast.csv") {
  const csv = citiesToCSV(cities);
  const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}
