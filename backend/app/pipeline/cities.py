"""
Registry of Ethiopian cities with geographic coordinates and climatic regions.
Enables geo-targeted queries for secondary fallback weather providers (e.g. Open-Meteo).
"""
from typing import Dict, Any, List

ETHIOPIAN_CITIES: Dict[str, Dict[str, Any]] = {
    "Addis Ababa": {
        "name": "Addis Ababa",
        "region": "Central Highlands",
        "latitude": 9.02,
        "longitude": 38.74,
        "elevation": 2355,
    },
    "Debre Birhan": {
        "name": "Debre Birhan",
        "region": "Central Highlands",
        "latitude": 9.68,
        "longitude": 39.53,
        "elevation": 2840,
    },
    "Bahir Dar": {
        "name": "Bahir Dar",
        "region": "Northern Highlands",
        "latitude": 11.59,
        "longitude": 37.39,
        "elevation": 1800,
    },
    "Gondar": {
        "name": "Gondar",
        "region": "Northern Highlands",
        "latitude": 12.60,
        "longitude": 37.47,
        "elevation": 2133,
    },
    "Mekelle": {
        "name": "Mekelle",
        "region": "Northern Highlands",
        "latitude": 13.50,
        "longitude": 39.47,
        "elevation": 2084,
    },
    "Axum": {
        "name": "Axum",
        "region": "Northern Highlands",
        "latitude": 14.13,
        "longitude": 38.72,
        "elevation": 2131,
    },
    "Dessie": {
        "name": "Dessie",
        "region": "Northern Highlands",
        "latitude": 11.13,
        "longitude": 39.63,
        "elevation": 2470,
    },
    "Hawassa": {
        "name": "Hawassa",
        "region": "Rift Valley",
        "latitude": 7.06,
        "longitude": 38.48,
        "elevation": 1708,
    },
    "Adama": {
        "name": "Adama",
        "region": "Rift Valley",
        "latitude": 8.54,
        "longitude": 39.27,
        "elevation": 1712,
    },
    "Arba Minch": {
        "name": "Arba Minch",
        "region": "Rift Valley",
        "latitude": 6.03,
        "longitude": 37.55,
        "elevation": 1285,
    },
    "Jimma": {
        "name": "Jimma",
        "region": "Southwestern Highlands",
        "latitude": 7.67,
        "longitude": 36.83,
        "elevation": 1780,
    },
    "Nekemte": {
        "name": "Nekemte",
        "region": "Western Highlands",
        "latitude": 9.09,
        "longitude": 36.55,
        "elevation": 2088,
    },
    "Dire Dawa": {
        "name": "Dire Dawa",
        "region": "Eastern Lowlands",
        "latitude": 9.60,
        "longitude": 41.87,
        "elevation": 1276,
    },
    "Jijiga": {
        "name": "Jijiga",
        "region": "Eastern Lowlands",
        "latitude": 9.35,
        "longitude": 42.80,
        "elevation": 1609,
    },
    "Semera": {
        "name": "Semera",
        "region": "Afar Lowlands",
        "latitude": 11.79,
        "longitude": 41.01,
        "elevation": 433,
    },
    "Gambela": {
        "name": "Gambela",
        "region": "Western Lowlands",
        "latitude": 8.25,
        "longitude": 34.58,
        "elevation": 526,
    },
    "Assosa": {
        "name": "Assosa",
        "region": "Western Lowlands",
        "latitude": 10.07,
        "longitude": 34.53,
        "elevation": 1570,
    },
    "Robe": {
        "name": "Robe",
        "region": "Bale Highlands",
        "latitude": 7.12,
        "longitude": 40.00,
        "elevation": 2492,
    },
}


def get_all_cities() -> List[Dict[str, Any]]:
    return list(ETHIOPIAN_CITIES.values())


def get_city_coords(city_name: str) -> Dict[str, Any]:
    return ETHIOPIAN_CITIES.get(city_name)
