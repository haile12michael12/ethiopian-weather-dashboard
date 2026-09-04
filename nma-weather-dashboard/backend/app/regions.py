"""
The scraper table only stores City + temps/conditions (no region), so we
enrich with a static lookup for the frontend's region filter. Extend this
as new cities show up in the NMA table.
"""
REGION_BY_CITY = {
    "Addis Ababa": "Central Highlands",
    "Debre Birhan": "Central Highlands",
    "Bahir Dar": "Northern Highlands",
    "Gondar": "Northern Highlands",
    "Mekelle": "Northern Highlands",
    "Axum": "Northern Highlands",
    "Dessie": "Northern Highlands",
    "Hawassa": "Rift Valley",
    "Adama": "Rift Valley",
    "Arba Minch": "Rift Valley",
    "Jimma": "Southwestern Highlands",
    "Nekemte": "Western Highlands",
    "Dire Dawa": "Eastern Lowlands",
    "Jijiga": "Eastern Lowlands",
    "Semera": "Afar Lowlands",
}


def region_for(city: str) -> str:
    return REGION_BY_CITY.get(city.strip(), "Ethiopia")
