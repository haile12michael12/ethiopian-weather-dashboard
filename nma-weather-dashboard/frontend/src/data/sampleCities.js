// Fallback data, used when the backend API is unreachable (e.g. first run
// before the Airflow DAG has populated the database, or local UI dev).
// Shape mirrors what GET /api/forecast returns.

export const SAMPLE_FORECAST = {
  as_of: "Sample data — connect the API for live NMA figures",
  source: "National Meteorology Agency",
  cities: [
    { id: 1, name: "Addis Ababa", region: "Central Highlands", days: [
      { label: "Today", min: 11, max: 22, condition: "Partly Cloudy" },
      { label: "Tomorrow", min: 10, max: 21, condition: "Scattered Showers" },
      { label: "Day 3", min: 12, max: 23, condition: "Mostly Sunny" },
    ]},
    { id: 2, name: "Debre Birhan", region: "Central Highlands", days: [
      { label: "Today", min: 7, max: 18, condition: "Cloudy" },
      { label: "Tomorrow", min: 6, max: 17, condition: "Rain Showers" },
      { label: "Day 3", min: 8, max: 19, condition: "Partly Cloudy" },
    ]},
    { id: 3, name: "Bahir Dar", region: "Northern Highlands", days: [
      { label: "Today", min: 15, max: 27, condition: "Sunny" },
      { label: "Tomorrow", min: 16, max: 28, condition: "Mostly Sunny" },
      { label: "Day 3", min: 15, max: 26, condition: "Partly Cloudy" },
    ]},
    { id: 4, name: "Gondar", region: "Northern Highlands", days: [
      { label: "Today", min: 14, max: 28, condition: "Sunny" },
      { label: "Tomorrow", min: 14, max: 29, condition: "Sunny" },
      { label: "Day 3", min: 15, max: 27, condition: "Mostly Sunny" },
    ]},
    { id: 5, name: "Mekelle", region: "Northern Highlands", days: [
      { label: "Today", min: 12, max: 25, condition: "Mostly Sunny" },
      { label: "Tomorrow", min: 11, max: 24, condition: "Partly Cloudy" },
      { label: "Day 3", min: 12, max: 25, condition: "Sunny" },
    ]},
    { id: 6, name: "Axum", region: "Northern Highlands", days: [
      { label: "Today", min: 13, max: 27, condition: "Sunny" },
      { label: "Tomorrow", min: 13, max: 28, condition: "Sunny" },
      { label: "Day 3", min: 14, max: 26, condition: "Mostly Sunny" },
    ]},
    { id: 7, name: "Dessie", region: "Northern Highlands", days: [
      { label: "Today", min: 10, max: 23, condition: "Partly Cloudy" },
      { label: "Tomorrow", min: 9, max: 22, condition: "Cloudy" },
      { label: "Day 3", min: 10, max: 23, condition: "Mostly Sunny" },
    ]},
    { id: 8, name: "Hawassa", region: "Rift Valley", days: [
      { label: "Today", min: 15, max: 27, condition: "Partly Cloudy" },
      { label: "Tomorrow", min: 14, max: 26, condition: "Thunderstorms" },
      { label: "Day 3", min: 15, max: 27, condition: "Scattered Showers" },
    ]},
    { id: 9, name: "Adama", region: "Rift Valley", days: [
      { label: "Today", min: 16, max: 29, condition: "Sunny" },
      { label: "Tomorrow", min: 16, max: 30, condition: "Mostly Sunny" },
      { label: "Day 3", min: 17, max: 29, condition: "Partly Cloudy" },
    ]},
    { id: 10, name: "Arba Minch", region: "Rift Valley", days: [
      { label: "Today", min: 18, max: 31, condition: "Mostly Sunny" },
      { label: "Tomorrow", min: 18, max: 30, condition: "Thunderstorms" },
      { label: "Day 3", min: 17, max: 29, condition: "Rain Showers" },
    ]},
    { id: 11, name: "Jimma", region: "Southwestern Highlands", days: [
      { label: "Today", min: 13, max: 24, condition: "Rain Showers" },
      { label: "Tomorrow", min: 13, max: 23, condition: "Thunderstorms" },
      { label: "Day 3", min: 14, max: 24, condition: "Scattered Showers" },
    ]},
    { id: 12, name: "Nekemte", region: "Western Highlands", days: [
      { label: "Today", min: 12, max: 23, condition: "Cloudy" },
      { label: "Tomorrow", min: 12, max: 22, condition: "Rain Showers" },
      { label: "Day 3", min: 13, max: 23, condition: "Partly Cloudy" },
    ]},
    { id: 13, name: "Dire Dawa", region: "Eastern Lowlands", days: [
      { label: "Today", min: 22, max: 34, condition: "Sunny" },
      { label: "Tomorrow", min: 23, max: 35, condition: "Sunny" },
      { label: "Day 3", min: 22, max: 34, condition: "Mostly Sunny" },
    ]},
    { id: 14, name: "Jijiga", region: "Eastern Lowlands", days: [
      { label: "Today", min: 15, max: 26, condition: "Partly Cloudy" },
      { label: "Tomorrow", min: 14, max: 25, condition: "Cloudy" },
      { label: "Day 3", min: 15, max: 26, condition: "Mostly Sunny" },
    ]},
    { id: 15, name: "Semera", region: "Afar Lowlands", days: [
      { label: "Today", min: 27, max: 41, condition: "Sunny" },
      { label: "Tomorrow", min: 28, max: 42, condition: "Sunny" },
      { label: "Day 3", min: 27, max: 40, condition: "Sunny" },
    ]},
  ],
};
