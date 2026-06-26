import requests

# We use the geocoder Nominatim API to get bounding box coordinates for a city
NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"

def geocode_city_to_bounding_box(city: str, country: str) -> str:
    """
    Convert a city name into an Overpass compatible bounding box

    Nominatim returns boundingbox as: [south, north, west, east]
    Overpass expects bounding boxes as: south, west, north, east
    """

    # Make Nominatim API request to get bounding box - specify results in json format
    response = requests.get(
        NOMINATIM_URL,
        params={"city": city, "country": country, "format": "json", "limit": 1},
        headers={'Accept': 'application/json', 'Content-Type': 'text/plain', 'User-Agent': "ai-trip-planner/0.1"},
        timeout=30,
    )

    response.raise_for_status()
    results = response.json()

    if not results:
        raise ValueError(f"Could not find a location for city: {city}")

    bounding_box = results[0]["boundingbox"]

    south = bounding_box[0]
    north = bounding_box[1]
    west = bounding_box[2]
    east = bounding_box[3]

    return f"{south},{west},{north},{east}"