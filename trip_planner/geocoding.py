import math
import requests
from trip_planner.models import GeocodedLocation

# We use the geocoder Nominatim API to get bounding box coordinates for a city
NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"

def geocode_city_to_location(city: str, country: str) -> GeocodedLocation:
    """
    Convert a city & country into a geocoded location with a:
        - Display name
        - City center latitude and longitude
        - Overpass compatible bounding box

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

    # Center points of the city
    latitude = float(results[0]["lat"])
    longitude = float(results[0]["lon"])

    # Create a bounding box around the center point with a radius of 8 km
    bounding_box = build_bounding_box_around_center(latitude, longitude, radius_km=8)

    return GeocodedLocation(
        display_name=results[0]["display_name"],
        latitude=latitude,
        longitude=longitude,
        bounding_box=bounding_box,
    )

def build_bounding_box_around_center(latitude: float, longitude: float, radius_km: float) -> str:
    """
    Build a bounding box around a center point (latitude, longitude) with a given radius in kilometers.
    Returns Overpass suitable bounding box: south, west, north, east
    """
    km_per_degree_latitude = 111.32
    latitude_delta = radius_km / km_per_degree_latitude

    km_per_degree_longitude = km_per_degree_latitude * math.cos(math.radians(latitude))
    longitude_delta = radius_km / km_per_degree_longitude

    south = latitude - latitude_delta
    north = latitude + latitude_delta
    west = longitude - longitude_delta
    east = longitude + longitude_delta

    return f"{south},{west},{north},{east}"